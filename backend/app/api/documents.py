import tempfile
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.database import get_session
from app.models import AIOutput, Document, DocumentChunk, User
from app.services.chunker import chunk_document
from app.services.document_parser import clean_text, parse_docx, parse_pdf
from app.services.evaluator import latest_evaluation
from app.utils.ids import new_id
from app.utils.text_utils import slug_title


router = APIRouter(prefix="/api/documents", tags=["documents"])


def document_json(session: Session, document: Document) -> dict:
    chunks_count = session.scalar(select(func.count()).select_from(DocumentChunk).where(DocumentChunk.document_id == document.id))
    output_ids = session.scalars(select(AIOutput.id).where(AIOutput.document_id == document.id)).all()
    evaluations = [latest_evaluation(session, output_id) for output_id in output_ids]
    scores = [row.trust_score for row in evaluations if row]
    return {
        "id": document.id, "user_id": document.user_id, "title": document.title,
        "source_type": document.source_type, "file_type": document.file_type,
        "raw_text": document.raw_text, "word_count": document.word_count,
        "page_count": document.page_count, "processing_status": document.processing_status,
        "created_at": document.created_at, "chunks_count": chunks_count or 0,
        "average_trust_score": round(sum(scores) / len(scores), 1) if scores else None,
    }


@router.post("/upload")
async def upload_document(file: UploadFile = File(...), user_id: str = "demo-user", session: Session = Depends(get_session)):
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in {".txt", ".md", ".pdf", ".docx"}:
        raise HTTPException(400, "Supported formats: TXT, MD, PDF, DOCX")
    if not session.get(User, user_id):
        session.add(User(id=user_id, name="Local User", persona="student_professional"))
        session.flush()
    content = await file.read()
    page_count = 1
    if suffix in {".txt", ".md"}:
        text = clean_text(content.decode("utf-8", errors="replace"))
    else:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(content)
            tmp_path = tmp.name
        try:
            if suffix == ".pdf":
                text, page_count = parse_pdf(tmp_path)
            else:
                text = parse_docx(tmp_path)
        finally:
            Path(tmp_path).unlink(missing_ok=True)
    document = Document(
        id=new_id("doc"), user_id=user_id, title=slug_title(text), source_type="upload",
        file_type=suffix.lstrip("."), raw_text=text, word_count=len(text.split()),
        page_count=page_count, processing_status="ready",
    )
    session.add(document)
    session.flush()
    for item in chunk_document(text):
        session.add(DocumentChunk(id=new_id("chunk"), document_id=document.id, **item, embedding_ref="lexical-local"))
    session.commit()
    return document_json(session, document)


@router.get("")
def list_documents(session: Session = Depends(get_session)):
    return [document_json(session, item) for item in session.scalars(select(Document).order_by(Document.created_at.desc())).all()]


@router.get("/{document_id}")
def get_document(document_id: str, session: Session = Depends(get_session)):
    document = session.get(Document, document_id)
    if not document:
        raise HTTPException(404, "Document not found")
    return document_json(session, document)


@router.get("/{document_id}/chunks")
def get_chunks(document_id: str, session: Session = Depends(get_session)):
    return [
        {
            "id": item.id, "chunk_index": item.chunk_index, "page_number": item.page_number,
            "section_title": item.section_title, "text": item.text, "token_estimate": item.token_estimate,
        }
        for item in session.scalars(select(DocumentChunk).where(DocumentChunk.document_id == document_id).order_by(DocumentChunk.chunk_index)).all()
    ]


@router.delete("/{document_id}")
def delete_document(document_id: str, session: Session = Depends(get_session)):
    document = session.get(Document, document_id)
    if not document:
        raise HTTPException(404, "Document not found")
    session.execute(delete(DocumentChunk).where(DocumentChunk.document_id == document_id))
    session.execute(delete(AIOutput).where(AIOutput.document_id == document_id))
    session.delete(document)
    session.commit()
    return {"status": "deleted"}

