from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_session
from app.models import ClaimCheck, DocumentChunk, EvaluationRun, MissingTopic
from app.services.evaluator import evaluate_output, latest_evaluation, trust_card


router = APIRouter(tags=["evaluation"])


@router.post("/api/evaluate/{output_id}")
def evaluate(output_id: str, session: Session = Depends(get_session)):
    try:
        return evaluate_output(session, output_id)
    except ValueError as exc:
        raise HTTPException(404, str(exc)) from exc


@router.get("/api/evaluations/{evaluation_id}")
def get_evaluation(evaluation_id: str, session: Session = Depends(get_session)):
    evaluation = session.get(EvaluationRun, evaluation_id)
    if not evaluation:
        raise HTTPException(404, "Evaluation not found")
    return trust_card(session, evaluation.output_id)


@router.get("/api/outputs/{output_id}/trust-card")
def get_trust_card(output_id: str, session: Session = Depends(get_session)):
    card = trust_card(session, output_id)
    if not card:
        raise HTTPException(404, "Output has not been evaluated")
    return card


@router.get("/api/outputs/{output_id}/claims")
def get_claims(output_id: str, session: Session = Depends(get_session)):
    evaluation = latest_evaluation(session, output_id)
    if not evaluation:
        return []
    claims = session.scalars(select(ClaimCheck).where(ClaimCheck.evaluation_run_id == evaluation.id)).all()
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


@router.get("/api/outputs/{output_id}/missing-topics")
def get_missing_topics(output_id: str, session: Session = Depends(get_session)):
    evaluation = latest_evaluation(session, output_id)
    if not evaluation:
        return []
    return [
        {"id": item.id, "topic": item.topic, "importance_score": item.importance_score, "reason": item.reason}
        for item in session.scalars(select(MissingTopic).where(MissingTopic.evaluation_run_id == evaluation.id)).all()
    ]

