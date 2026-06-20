from typing import Literal

from pydantic import BaseModel, Field


class GenerationRequest(BaseModel):
    document_id: str
    user_id: str = "demo-user"
    prompt: str = ""


class AskRequest(GenerationRequest):
    prompt: str = Field(min_length=2)


class FeedbackRequest(BaseModel):
    user_id: str = "demo-user"
    output_id: str
    feedback_type: Literal[
        "correct",
        "wrong",
        "missing_key_point",
        "too_long",
        "too_short",
        "bad_tone",
        "not_useful",
        "great_output",
        "needs_citation",
    ]
    comment: str = ""


class LearningRecomputeRequest(BaseModel):
    user_id: str = "demo-user"
