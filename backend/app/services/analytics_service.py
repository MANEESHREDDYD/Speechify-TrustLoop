from collections import Counter, defaultdict

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import AIOutput, Document, EvaluationRun, MissingTopic, UserFeedback


def overview(session: Session) -> dict:
    documents = session.scalars(select(Document)).all()
    outputs = session.scalars(select(AIOutput)).all()
    evaluations = session.scalars(select(EvaluationRun)).all()
    topics = session.scalars(select(MissingTopic)).all()
    feedback = session.scalars(select(UserFeedback)).all()
    return {
        "documents_count": len(documents),
        "outputs_count": len(outputs),
        "evaluations_count": len(evaluations),
        "average_trust_score": round(sum(e.trust_score for e in evaluations) / max(1, len(evaluations)), 1),
        "average_hallucination_risk": round(sum(e.hallucination_risk for e in evaluations) / max(1, len(evaluations)), 3),
        "most_common_missing_topics": [topic for topic, _ in Counter(t.topic for t in topics).most_common(6)],
        "feedback_distribution": dict(Counter(item.feedback_type for item in feedback)),
    }


def by_output_type(session: Session) -> list[dict]:
    outputs = {output.id: output for output in session.scalars(select(AIOutput)).all()}
    grouped: dict[str, list[EvaluationRun]] = defaultdict(list)
    for evaluation in session.scalars(select(EvaluationRun)).all():
        if evaluation.output_id in outputs:
            grouped[outputs[evaluation.output_id].output_type].append(evaluation)
    return [
        {
            "output_type": key,
            "average_trust_score": round(sum(row.trust_score for row in rows) / len(rows), 1),
            "average_hallucination_risk": round(sum(row.hallucination_risk for row in rows) / len(rows), 3),
            "evaluations": len(rows),
        }
        for key, rows in sorted(grouped.items())
    ]


def common_missing_topics(session: Session) -> list[dict]:
    rows = session.scalars(select(MissingTopic)).all()
    return [{"topic": topic, "count": count} for topic, count in Counter(r.topic for r in rows).most_common(10)]

