from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_session
from app.models import AIOutput, Document
from app.schemas import AskRequest, GenerationRequest
from app.services.evaluator import trust_card
from app.services.generator import GENERATORS, answer_document_question
from app.utils.ids import new_id


router = APIRouter(tags=["generation"])


def output_json(session: Session, output: AIOutput) -> dict:
    return {
        "id": output.id,
        "output_id": output.id,
        "document_id": output.document_id,
        "user_id": output.user_id,
        "output_type": output.output_type,
        "prompt": output.prompt,
        "generated_text": output.generated_text,
        "generation_mode": output.generation_mode,
        "created_at": output.created_at,
        "trust_card": trust_card(session, output.id),
    }


def create_output(session: Session, request: GenerationRequest, output_type: str) -> dict:
    document = session.get(Document, request.document_id)
    if not document:
        raise HTTPException(404, "Document not found")
    generator = GENERATORS[output_type]
    output = AIOutput(
        id=new_id("out"),
        document_id=document.id,
        user_id=request.user_id,
        output_type=output_type,
        prompt=request.prompt,
        generated_text=generator(document.raw_text),
        generation_mode="deterministic",
    )
    session.add(output)
    session.commit()
    return output_json(session, output)


@router.post("/api/generate/summary")
def summary(request: GenerationRequest, session: Session = Depends(get_session)):
    return create_output(session, request, "summary")


@router.post("/api/generate/key-points")
def key_points(request: GenerationRequest, session: Session = Depends(get_session)):
    return create_output(session, request, "key_points")


@router.post("/api/generate/quiz")
def quiz(request: GenerationRequest, session: Session = Depends(get_session)):
    return create_output(session, request, "quiz")


@router.post("/api/generate/podcast-script")
def podcast(request: GenerationRequest, session: Session = Depends(get_session)):
    return create_output(session, request, "podcast_script")


@router.post("/api/generate/meeting-notes")
def meeting_notes(request: GenerationRequest, session: Session = Depends(get_session)):
    return create_output(session, request, "meeting_notes")


@router.post("/api/generate/work-report")
def work_report(request: GenerationRequest, session: Session = Depends(get_session)):
    return create_output(session, request, "work_report")


@router.post("/api/ask")
def ask(request: AskRequest, session: Session = Depends(get_session)):
    document = session.get(Document, request.document_id)
    if not document:
        raise HTTPException(404, "Document not found")
    output = AIOutput(
        id=new_id("out"),
        document_id=document.id,
        user_id=request.user_id,
        output_type="ask_document",
        prompt=request.prompt,
        generated_text=answer_document_question(document.raw_text, request.prompt),
        generation_mode="deterministic",
    )
    session.add(output)
    session.commit()
    return output_json(session, output)


@router.get("/api/outputs")
def list_outputs(document_id: str | None = None, session: Session = Depends(get_session)):
    query = select(AIOutput).order_by(AIOutput.created_at.desc())
    if document_id:
        query = query.where(AIOutput.document_id == document_id)
    return [output_json(session, item) for item in session.scalars(query).all()]


@router.get("/api/outputs/{output_id}")
def get_output(output_id: str, session: Session = Depends(get_session)):
    output = session.get(AIOutput, output_id)
    if not output:
        raise HTTPException(404, "Output not found")
    return output_json(session, output)

