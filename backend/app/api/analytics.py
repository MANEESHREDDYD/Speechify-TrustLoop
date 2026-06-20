from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_session
from app.services.analytics_service import by_output_type, common_missing_topics, overview
from app.services.feedback_service import feedback_summary


router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/overview")
def analytics_overview(session: Session = Depends(get_session)):
    return overview(session)


@router.get("/trust-by-output-type")
def trust_by_type(session: Session = Depends(get_session)):
    return by_output_type(session)


@router.get("/hallucination-risk")
def hallucination_risk(session: Session = Depends(get_session)):
    return [
        {"output_type": item["output_type"], "hallucination_risk": item["average_hallucination_risk"]}
        for item in by_output_type(session)
    ]


@router.get("/missing-topics")
def missing_topics(session: Session = Depends(get_session)):
    return common_missing_topics(session)


@router.get("/user-feedback")
def user_feedback(session: Session = Depends(get_session)):
    return feedback_summary(session)

