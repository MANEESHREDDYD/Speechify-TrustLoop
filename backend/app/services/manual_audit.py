from sqlalchemy.orm import Session

from app.models import AIOutput, Document, DocumentChunk, User
from app.services.chunker import chunk_document
from app.services.evaluator import (
    claim_results,
    evaluate_output,
    missing_topic_results,
    trust_card,
)
from app.utils.ids import new_id


def run_manual_audit(
    session: Session,
    *,
    user_id: str,
    source_title: str,
    source_text: str,
    output_type: str,
    generated_text: str,
) -> dict:
    if not session.get(User, user_id):
        session.add(User(id=user_id, name="Manual Audit User", persona="local_reviewer"))
        session.flush()

    document = Document(
        id=new_id("doc"),
        user_id=user_id,
        title=source_title.strip(),
        source_type="manual_audit",
        file_type="txt",
        raw_text=source_text.strip(),
        word_count=len(source_text.split()),
        page_count=1,
        processing_status="ready",
    )
    session.add(document)
    session.flush()

    for item in chunk_document(document.raw_text):
        session.add(
            DocumentChunk(
                id=new_id("chunk"),
                document_id=document.id,
                **item,
                retrieval_ref="lexical-only",
            )
        )

    output = AIOutput(
        id=new_id("out"),
        document_id=document.id,
        user_id=user_id,
        output_type=output_type,
        prompt="Pasted external output for manual audit",
        generated_text=generated_text.strip(),
        generation_mode="external_manual",
    )
    session.add(output)
    session.flush()

    evaluation = evaluate_output(session, output.id)
    return {
        "document_id": document.id,
        "output_id": output.id,
        "evaluation_id": evaluation["evaluation_id"],
        "trust_card": trust_card(session, output.id),
        "claim_checks": claim_results(session, output.id),
        "missing_topics": missing_topic_results(session, output.id),
    }
