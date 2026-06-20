from datetime import datetime, timezone

from sqlalchemy import Float, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class User(Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(Text, primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    persona: Mapped[str] = mapped_column(Text)
    created_at: Mapped[str] = mapped_column(Text, default=now_iso)


class Document(Base):
    __tablename__ = "documents"
    id: Mapped[str] = mapped_column(Text, primary_key=True)
    user_id: Mapped[str] = mapped_column(Text, ForeignKey("users.id"))
    title: Mapped[str] = mapped_column(Text)
    source_type: Mapped[str] = mapped_column(Text)
    file_type: Mapped[str] = mapped_column(Text)
    raw_text: Mapped[str] = mapped_column(Text)
    word_count: Mapped[int] = mapped_column(Integer)
    page_count: Mapped[int] = mapped_column(Integer, default=1)
    processing_status: Mapped[str] = mapped_column(Text, default="ready")
    created_at: Mapped[str] = mapped_column(Text, default=now_iso)


class DocumentChunk(Base):
    __tablename__ = "document_chunks"
    id: Mapped[str] = mapped_column(Text, primary_key=True)
    document_id: Mapped[str] = mapped_column(Text, ForeignKey("documents.id"))
    chunk_index: Mapped[int] = mapped_column(Integer)
    page_number: Mapped[int] = mapped_column(Integer, default=1)
    section_title: Mapped[str] = mapped_column(Text, default="")
    text: Mapped[str] = mapped_column(Text)
    token_estimate: Mapped[int] = mapped_column(Integer)
    embedding_ref: Mapped[str] = mapped_column(Text, default="lexical-local")
    created_at: Mapped[str] = mapped_column(Text, default=now_iso)


class AIOutput(Base):
    __tablename__ = "ai_outputs"
    id: Mapped[str] = mapped_column(Text, primary_key=True)
    document_id: Mapped[str] = mapped_column(Text, ForeignKey("documents.id"))
    user_id: Mapped[str] = mapped_column(Text, ForeignKey("users.id"))
    output_type: Mapped[str] = mapped_column(Text)
    prompt: Mapped[str] = mapped_column(Text, default="")
    generated_text: Mapped[str] = mapped_column(Text)
    generation_mode: Mapped[str] = mapped_column(Text, default="deterministic")
    created_at: Mapped[str] = mapped_column(Text, default=now_iso)


class EvaluationRun(Base):
    __tablename__ = "evaluation_runs"
    id: Mapped[str] = mapped_column(Text, primary_key=True)
    output_id: Mapped[str] = mapped_column(Text, ForeignKey("ai_outputs.id"))
    document_id: Mapped[str] = mapped_column(Text, ForeignKey("documents.id"))
    grounding_score: Mapped[float] = mapped_column(Float)
    coverage_score: Mapped[float] = mapped_column(Float)
    citation_score: Mapped[float] = mapped_column(Float)
    readability_score: Mapped[float] = mapped_column(Float)
    hallucination_risk: Mapped[float] = mapped_column(Float)
    action_item_score: Mapped[float] = mapped_column(Float, default=0.8)
    quiz_relevance_score: Mapped[float] = mapped_column(Float, default=0.8)
    trust_score: Mapped[float] = mapped_column(Float)
    created_at: Mapped[str] = mapped_column(Text, default=now_iso)


class ClaimCheck(Base):
    __tablename__ = "claim_checks"
    id: Mapped[str] = mapped_column(Text, primary_key=True)
    evaluation_run_id: Mapped[str] = mapped_column(Text, ForeignKey("evaluation_runs.id"))
    claim_text: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(Text)
    confidence: Mapped[float] = mapped_column(Float)
    supporting_chunk_id: Mapped[str | None] = mapped_column(Text, nullable=True)
    supporting_text: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[str] = mapped_column(Text, default=now_iso)


class MissingTopic(Base):
    __tablename__ = "missing_topics"
    id: Mapped[str] = mapped_column(Text, primary_key=True)
    evaluation_run_id: Mapped[str] = mapped_column(Text, ForeignKey("evaluation_runs.id"))
    topic: Mapped[str] = mapped_column(Text)
    importance_score: Mapped[float] = mapped_column(Float)
    reason: Mapped[str] = mapped_column(Text)


class UserFeedback(Base):
    __tablename__ = "user_feedback"
    id: Mapped[str] = mapped_column(Text, primary_key=True)
    user_id: Mapped[str] = mapped_column(Text, ForeignKey("users.id"))
    output_id: Mapped[str] = mapped_column(Text, ForeignKey("ai_outputs.id"))
    feedback_type: Mapped[str] = mapped_column(Text)
    comment: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[str] = mapped_column(Text, default=now_iso)


class LearningMemory(Base):
    __tablename__ = "learning_memory"
    id: Mapped[str] = mapped_column(Text, primary_key=True)
    user_id: Mapped[str] = mapped_column(Text, ForeignKey("users.id"))
    topic: Mapped[str] = mapped_column(Text)
    strength_score: Mapped[float] = mapped_column(Float, default=0.5)
    quiz_accuracy: Mapped[float] = mapped_column(Float, default=0.0)
    last_seen_at: Mapped[str] = mapped_column(Text, default=now_iso)
    source_document_count: Mapped[int] = mapped_column(Integer, default=1)


class AnalyticsEvent(Base):
    __tablename__ = "analytics_events"
    id: Mapped[str] = mapped_column(Text, primary_key=True)
    user_id: Mapped[str] = mapped_column(Text)
    event_type: Mapped[str] = mapped_column(Text)
    entity_type: Mapped[str] = mapped_column(Text)
    entity_id: Mapped[str] = mapped_column(Text)
    metadata_json: Mapped[str] = mapped_column(Text, default="{}")
    created_at: Mapped[str] = mapped_column(Text, default=now_iso)

