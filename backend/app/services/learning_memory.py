from collections import defaultdict

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models import AIOutput, Document, EvaluationRun, LearningMemory, MissingTopic, UserFeedback, now_iso
from app.services.topic_extractor import extract_topics
from app.utils.ids import new_id


def recompute_learning_memory(session: Session, user_id: str) -> dict:
    scores: dict[str, list[float]] = defaultdict(list)
    documents = session.scalars(select(Document).where(Document.user_id == user_id)).all()
    for document in documents:
        for topic in extract_topics(document.raw_text, 8):
            scores[topic["topic"]].append(0.55)
    outputs = session.scalars(select(AIOutput).where(AIOutput.user_id == user_id)).all()
    for output in outputs:
        if output.output_type == "quiz":
            for topic in extract_topics(output.generated_text, 6):
                scores[topic["topic"]].append(0.78)
        evaluations = session.scalars(select(EvaluationRun).where(EvaluationRun.output_id == output.id)).all()
        for evaluation in evaluations:
            missing = session.scalars(select(MissingTopic).where(MissingTopic.evaluation_run_id == evaluation.id)).all()
            for item in missing:
                scores[item.topic].append(0.25)
    feedback = session.scalars(select(UserFeedback).where(UserFeedback.user_id == user_id)).all()
    for item in feedback:
        if item.feedback_type == "missing_key_point" and item.comment:
            for topic in extract_topics(item.comment, 3):
                scores[topic["topic"]].append(0.2)

    session.execute(delete(LearningMemory).where(LearningMemory.user_id == user_id))
    for topic, values in scores.items():
        strength = sum(values) / len(values)
        session.add(
            LearningMemory(
                id=new_id("memory"),
                user_id=user_id,
                topic=topic,
                strength_score=round(strength, 3),
                quiz_accuracy=round(max(0.0, strength - 0.1), 3),
                last_seen_at=now_iso(),
                source_document_count=len(values),
            )
        )
    session.commit()
    return get_learning_memory(session, user_id)


def get_learning_memory(session: Session, user_id: str) -> dict:
    memories = session.scalars(
        select(LearningMemory).where(LearningMemory.user_id == user_id).order_by(LearningMemory.strength_score.desc())
    ).all()
    strong = [{"topic": m.topic, "strength_score": m.strength_score} for m in memories if m.strength_score >= 0.6][:8]
    weak = [{"topic": m.topic, "strength_score": m.strength_score} for m in reversed(memories) if m.strength_score < 0.6][:8]
    recap = [
        f"Review {item['topic']} with a short source-grounded recap."
        for item in weak[:3]
    ] or ["Generate a quiz from a recent document to begin building learning memory."]
    return {
        "user_id": user_id,
        "strong_topics": strong,
        "weak_topics": weak,
        "recommended_recap": recap,
        "documents_studied": len(session.scalars(select(Document).where(Document.user_id == user_id)).all()),
    }
