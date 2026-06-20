from collections import Counter

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import UserFeedback
from app.utils.ids import new_id


def save_feedback(session: Session, user_id: str, output_id: str, feedback_type: str, comment: str = "") -> UserFeedback:
    feedback = UserFeedback(
        id=new_id("feedback"),
        user_id=user_id,
        output_id=output_id,
        feedback_type=feedback_type,
        comment=comment,
    )
    session.add(feedback)
    session.commit()
    return feedback


def feedback_summary(session: Session) -> dict:
    rows = session.scalars(select(UserFeedback)).all()
    return {
        "total": len(rows),
        "distribution": dict(Counter(row.feedback_type for row in rows)),
        "recent": [
            {
                "id": row.id,
                "output_id": row.output_id,
                "feedback_type": row.feedback_type,
                "comment": row.comment,
                "created_at": row.created_at,
            }
            for row in rows[-10:]
        ],
    }

