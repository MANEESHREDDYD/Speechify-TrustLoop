from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_session
from app.schemas import LearningRecomputeRequest
from app.services.learning_memory import get_learning_memory, recompute_learning_memory


router = APIRouter(prefix="/api/learning-memory", tags=["learning"])


@router.get("/{user_id}")
def memory(user_id: str, session: Session = Depends(get_session)):
    data = get_learning_memory(session, user_id)
    if not data["strong_topics"] and not data["weak_topics"]:
        data = recompute_learning_memory(session, user_id)
    return data


@router.get("/{user_id}/weak-topics")
def weak_topics(user_id: str, session: Session = Depends(get_session)):
    return {"user_id": user_id, "weak_topics": get_learning_memory(session, user_id)["weak_topics"]}


@router.post("/recompute")
def recompute(request: LearningRecomputeRequest, session: Session = Depends(get_session)):
    return recompute_learning_memory(session, request.user_id)

