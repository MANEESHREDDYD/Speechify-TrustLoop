from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.config import DEMO_DATA_DIR
from app.models import (
    AIOutput, AnalyticsEvent, ClaimCheck, Document, DocumentChunk, EvaluationRun,
    LearningMemory, MissingTopic, User, UserFeedback,
)
from app.services.chunker import chunk_document
from app.services.evaluator import evaluate_output
from app.services.generator import generate_meeting_notes, generate_summary, generate_work_report
from app.utils.ids import new_id
from app.utils.text_utils import slug_title


DEMO_FILES = {
    "student": ["student/ai_accessibility_chapter.txt", "student/dyslexia_learning_notes.txt", "student/machine_learning_intro.txt"],
    "meeting": ["meetings/product_launch_meeting_transcript.txt", "meetings/enterprise_customer_call_transcript.txt"],
    "work": ["work/market_analysis_source_pack.txt", "work/competitor_research_notes.txt", "work/q2_user_feedback.txt"],
    "podcast": ["podcast/audio_learning_article.txt", "podcast/productivity_voice_ai_article.txt"],
}


def reset_demo(session: Session) -> None:
    for model in (
        AnalyticsEvent, LearningMemory, UserFeedback, MissingTopic, ClaimCheck,
        EvaluationRun, AIOutput, DocumentChunk, Document, User,
    ):
        session.execute(delete(model))
    session.commit()


def _add_document(session: Session, relative: str, category: str) -> Document:
    text = (DEMO_DATA_DIR / relative).read_text(encoding="utf-8")
    document = Document(
        id=new_id("doc"),
        user_id="demo-user",
        title=slug_title(text),
        source_type=category,
        file_type="txt",
        raw_text=text,
        word_count=len(text.split()),
        page_count=1,
        processing_status="ready",
    )
    session.add(document)
    session.flush()
    for item in chunk_document(text):
        session.add(DocumentChunk(id=new_id("chunk"), document_id=document.id, **item, embedding_ref="lexical-local"))
    return document


def seed_demo(session: Session) -> dict:
    reset_demo(session)
    session.add(User(id="demo-user", name="Maneesh Demo User", persona="student_professional"))
    session.flush()
    docs: dict[str, Document] = {}
    for category, files in DEMO_FILES.items():
        for relative in files:
            docs[relative] = _add_document(session, relative, category)
    session.commit()

    starters = [
        (docs["student/ai_accessibility_chapter.txt"], "summary", generate_summary),
        (docs["meetings/product_launch_meeting_transcript.txt"], "meeting_notes", generate_meeting_notes),
        (docs["work/market_analysis_source_pack.txt"], "work_report", generate_work_report),
    ]
    all_ids = []
    for document, output_type, generator in starters:
        output = AIOutput(
            id=new_id("out"), document_id=document.id, user_id="demo-user",
            output_type=output_type, prompt="Seeded demo output",
            generated_text=generator(document.raw_text), generation_mode="deterministic",
        )
        session.add(output)
        session.commit()
        evaluate_output(session, output.id)
        all_ids.append(output.id)

    negative_specs = [
        ("meetings/product_launch_meeting_transcript.txt", "meeting_notes", "negative-tests/wrong_meeting_notes_output.txt"),
        ("podcast/audio_learning_article.txt", "podcast_script", "negative-tests/incomplete_podcast_output.txt"),
        ("student/ai_accessibility_chapter.txt", "summary", "negative-tests/hallucinated_summary_output.txt"),
    ]
    negative_ids = []
    for document_key, output_type, output_file in negative_specs:
        output = AIOutput(
            id=new_id("out"), document_id=docs[document_key].id, user_id="demo-user",
            output_type=output_type, prompt="Negative reliability test",
            generated_text=(DEMO_DATA_DIR / output_file).read_text(encoding="utf-8"),
            generation_mode="negative_test",
        )
        session.add(output)
        session.commit()
        evaluate_output(session, output.id)
        all_ids.append(output.id)
        negative_ids.append(output.id)
    return {
        "status": "seeded",
        "documents_count": len(docs),
        "outputs_count": len(all_ids),
        "negative_test_output_ids": negative_ids,
    }

