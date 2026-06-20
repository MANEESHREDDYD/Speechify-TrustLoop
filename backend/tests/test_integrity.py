from pathlib import Path

from sqlalchemy import func, select

from app.database import SessionLocal, engine
from app.models import (
    AIOutput,
    ClaimCheck,
    Document,
    DocumentChunk,
    EvaluationRun,
    MissingTopic,
    UserFeedback,
)


def test_tests_use_isolated_database_or_configured_test_db(test_database_path):
    configured_path = Path(engine.url.database).resolve()
    development_path = (Path(__file__).resolve().parents[1] / "s-trustloop.db").resolve()

    assert configured_path == test_database_path.resolve()
    assert configured_path != development_path
    assert "s-trustloop-tests-" in str(configured_path.parent)


def test_delete_document_removes_dependent_rows(seeded_client):
    with SessionLocal() as session:
        negative_output = session.scalar(
            select(AIOutput).where(
                AIOutput.output_type == "meeting_notes",
                AIOutput.generation_mode == "negative_test",
            )
        )
        document_id = negative_output.document_id
        output_ids = list(
            session.scalars(select(AIOutput.id).where(AIOutput.document_id == document_id)).all()
        )
        evaluation_ids = list(
            session.scalars(
                select(EvaluationRun.id).where(EvaluationRun.document_id == document_id)
            ).all()
        )

        assert output_ids
        assert evaluation_ids
        assert session.scalar(
            select(func.count())
            .select_from(ClaimCheck)
            .where(ClaimCheck.evaluation_run_id.in_(evaluation_ids))
        ) > 0
        assert session.scalar(
            select(func.count())
            .select_from(MissingTopic)
            .where(MissingTopic.evaluation_run_id.in_(evaluation_ids))
        ) > 0

    feedback_response = seeded_client.post(
        "/api/feedback",
        json={
            "user_id": "demo-user",
            "output_id": negative_output.id,
            "feedback_type": "wrong",
        },
    )
    assert feedback_response.status_code == 200

    response = seeded_client.delete(f"/api/documents/{document_id}")
    assert response.status_code == 200

    with SessionLocal() as session:
        assert session.get(Document, document_id) is None
        assert session.scalar(
            select(func.count())
            .select_from(DocumentChunk)
            .where(DocumentChunk.document_id == document_id)
        ) == 0
        assert session.scalar(
            select(func.count())
            .select_from(AIOutput)
            .where(AIOutput.document_id == document_id)
        ) == 0
        assert session.scalar(
            select(func.count())
            .select_from(EvaluationRun)
            .where(EvaluationRun.id.in_(evaluation_ids))
        ) == 0
        assert session.scalar(
            select(func.count())
            .select_from(ClaimCheck)
            .where(ClaimCheck.evaluation_run_id.in_(evaluation_ids))
        ) == 0
        assert session.scalar(
            select(func.count())
            .select_from(MissingTopic)
            .where(MissingTopic.evaluation_run_id.in_(evaluation_ids))
        ) == 0
        assert session.scalar(
            select(func.count())
            .select_from(UserFeedback)
            .where(UserFeedback.output_id.in_(output_ids))
        ) == 0


def test_feedback_does_not_change_existing_trust_score(seeded_client):
    output = next(
        row
        for row in seeded_client.get("/api/outputs").json()
        if row["output_type"] == "summary" and row["generation_mode"] == "deterministic"
    )
    before = output["trust_card"]["trust_score"]

    feedback_response = seeded_client.post(
        "/api/feedback",
        json={
            "user_id": "demo-user",
            "output_id": output["id"],
            "feedback_type": "wrong",
        },
    )
    assert feedback_response.status_code == 200

    after = seeded_client.post(f"/api/evaluate/{output['id']}").json()["trust_score"]
    assert after == before
