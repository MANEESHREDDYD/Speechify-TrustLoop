from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_session
from app.models import EvaluationRun
from app.services.evaluator import (
    claim_results,
    evaluate_output,
    missing_topic_results,
    trust_card,
)


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
    return claim_results(session, output_id)


@router.get("/api/outputs/{output_id}/missing-topics")
def get_missing_topics(output_id: str, session: Session = Depends(get_session)):
    return missing_topic_results(session, output_id)
