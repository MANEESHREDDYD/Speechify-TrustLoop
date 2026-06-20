from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_session
from app.models import AIOutput
from app.schemas import FeedbackRequest
from app.services.feedback_service import feedback_summary, save_feedback
from app.services.learning_memory import recompute_learning_memory


router = APIRouter(prefix="/api/feedback", tags=["feedback"])


@router.post("")
def create_feedback(request: FeedbackRequest, session: Session = Depends(get_session)):
    if not session.get(AIOutput, request.output_id):
        raise HTTPException(404, "Output not found")
    item = save_feedback(session, request.user_id, request.output_id, request.feedback_type, request.comment)
    recompute_learning_memory(session, request.user_id)
    return {
        "id": item.id,
        "user_id": item.user_id,
        "output_id": item.output_id,
        "feedback_type": item.feedback_type,
        "comment": item.comment,
        "created_at": item.created_at,
    }


@router.get("/summary")
def summary(session: Session = Depends(get_session)):
    return feedback_summary(session)

