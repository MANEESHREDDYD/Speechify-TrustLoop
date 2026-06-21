from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import AIOutput, ClaimCheck, Document, DocumentChunk, EvaluationRun, MissingTopic
from app.services.claim_checker import classify_claim, split_into_claims
from app.services.retrieval import retrieve_top_k
from app.services.topic_extractor import detect_missing_topics, extract_topics
from app.utils.ids import new_id
from app.utils.scoring import calculate_scores, trust_label


def evaluate_output(session: Session, output_id: str) -> dict:
    output = session.get(AIOutput, output_id)
    if not output:
        raise ValueError("Output not found")
    document = session.get(Document, output.document_id)
    if not document:
        raise ValueError("Source document not found")

    checks = []
    for claim in split_into_claims(output.generated_text):
        result = classify_claim(claim, retrieve_top_k(session, claim, document.id, 3))
        result["claim_text"] = claim
        checks.append(result)

    missing = detect_missing_topics(document.raw_text, output.generated_text)
    source_topics = extract_topics(document.raw_text, 12)
    scores = calculate_scores(checks, len(source_topics), len(missing), output.generated_text, output.output_type)
    evaluation = EvaluationRun(
        id=new_id("eval"),
        output_id=output.id,
        document_id=document.id,
        grounding_score=scores["grounding_score"],
        coverage_score=scores["coverage_score"],
        citation_score=scores["citation_score"],
        readability_score=scores["readability_score"],
        hallucination_risk=scores["hallucination_risk"],
        action_item_score=scores["action_item_score"],
        quiz_relevance_score=scores["quiz_relevance_score"],
        trust_score=scores["trust_score"],
    )
    session.add(evaluation)
    for check in checks:
        session.add(ClaimCheck(
            id=new_id("claim"),
            evaluation_run_id=evaluation.id,
            claim_text=check["claim_text"],
            status=check["status"],
            confidence=check["confidence"],
            supporting_chunk_id=check["supporting_chunk_id"],
            supporting_text=check["supporting_text"],
        ))
    for topic in missing:
        session.add(MissingTopic(
            id=new_id("topic"),
            evaluation_run_id=evaluation.id,
            topic=topic["topic"],
            importance_score=topic["importance_score"],
            reason=topic["reason"],
        ))
    session.commit()
    return {
        "evaluation_id": evaluation.id,
        "output_id": output.id,
        "output_type": output.output_type,
        "trust_score": scores["trust_score"],
        "label": trust_label(scores["trust_score"]),
        **{key: scores[key] for key in (
            "grounding_score", "coverage_score", "citation_score", "readability_score",
            "hallucination_risk", "supported_claims", "weakly_supported_claims",
            "unsupported_claims", "contradicted_claims",
        )},
        "missing_topics_count": len(missing),
    }


def latest_evaluation(session: Session, output_id: str) -> EvaluationRun | None:
    return session.scalars(
        select(EvaluationRun)
        .where(EvaluationRun.output_id == output_id)
        .order_by(EvaluationRun.created_at.desc())
    ).first()


def trust_card(session: Session, output_id: str) -> dict | None:
    evaluation = latest_evaluation(session, output_id)
    if not evaluation:
        return None
    checks = session.scalars(
        select(ClaimCheck).where(ClaimCheck.evaluation_run_id == evaluation.id)
    ).all()
    missing_count = len(session.scalars(
        select(MissingTopic).where(MissingTopic.evaluation_run_id == evaluation.id)
    ).all())
    counts = {status: sum(c.status == status for c in checks) for status in (
        "supported", "weakly_supported", "unsupported", "contradicted"
    )}
    return {
        "evaluation_id": evaluation.id,
        "output_id": output_id,
        "trust_score": evaluation.trust_score,
        "label": trust_label(evaluation.trust_score),
        "grounding_score": evaluation.grounding_score,
        "coverage_score": evaluation.coverage_score,
        "citation_score": evaluation.citation_score,
        "readability_score": evaluation.readability_score,
        "hallucination_risk": evaluation.hallucination_risk,
        "supported_claims": counts["supported"],
        "weakly_supported_claims": counts["weakly_supported"],
        "unsupported_claims": counts["unsupported"],
        "contradicted_claims": counts["contradicted"],
        "missing_topics_count": missing_count,
    }


def claim_results(session: Session, output_id: str) -> list[dict]:
    evaluation = latest_evaluation(session, output_id)
    if not evaluation:
        return []
    claims = session.scalars(
        select(ClaimCheck).where(ClaimCheck.evaluation_run_id == evaluation.id)
    ).all()
    result = []
    for claim in claims:
        chunk = session.get(DocumentChunk, claim.supporting_chunk_id) if claim.supporting_chunk_id else None
        result.append({
            "id": claim.id,
            "claim_text": claim.claim_text,
            "status": claim.status,
            "confidence": claim.confidence,
            "supporting_chunk_id": claim.supporting_chunk_id,
            "supporting_text": claim.supporting_text,
            "section_title": chunk.section_title if chunk else None,
            "page_number": chunk.page_number if chunk else None,
        })
    return result


def missing_topic_results(session: Session, output_id: str) -> list[dict]:
    evaluation = latest_evaluation(session, output_id)
    if not evaluation:
        return []
    return [
        {
            "id": item.id,
            "topic": item.topic,
            "importance_score": item.importance_score,
            "reason": item.reason,
        }
        for item in session.scalars(
            select(MissingTopic).where(MissingTopic.evaluation_run_id == evaluation.id)
        ).all()
    ]
