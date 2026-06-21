from pathlib import Path

from scripts.run_real_use_validation import run_validation


def manual_payload(**overrides):
    payload = {
        "user_id": "demo-user",
        "source_title": "External policy note",
        "source_text": (
            "Section 1: Access\nOnly approved reviewers may open the archive.\n\n"
            "Section 2: Retention\nThe archive must be deleted after thirty days.\n\n"
            "Section 3: Incidents\nA suspected leak must be reported within twenty-four hours."
        ),
        "output_type": "summary",
        "generated_text": (
            "# Summary\n\nOnly approved reviewers may open the archive. "
            "The archive must be deleted after thirty days. "
            "A suspected leak must be reported within twenty-four hours."
        ),
    }
    payload.update(overrides)
    return payload


def test_manual_audit_endpoint(client):
    response = client.post("/api/audit/manual", json=manual_payload())

    assert response.status_code == 200
    result = response.json()
    assert result["document_id"].startswith("doc_")
    assert result["output_id"].startswith("out_")
    assert result["evaluation_id"].startswith("eval_")
    assert result["trust_card"]["output_id"] == result["output_id"]
    assert result["claim_checks"]

    stored = client.get(f"/api/outputs/{result['output_id']}").json()
    assert stored["generation_mode"] == "external_manual"


def test_manual_audit_detects_unsupported_claim(client):
    response = client.post(
        "/api/audit/manual",
        json=manual_payload(
            generated_text=(
                "# Summary\n\nOnly approved reviewers may open the archive. "
                "The archive automatically proves that every reviewer is trustworthy."
            )
        ),
    )

    assert response.status_code == 200
    result = response.json()
    assert any(
        claim["status"] in {"unsupported", "contradicted"}
        and "automatically proves" in claim["claim_text"]
        for claim in result["claim_checks"]
    )


def test_manual_audit_detects_missing_topics(client):
    response = client.post(
        "/api/audit/manual",
        json=manual_payload(
            generated_text="# Summary\n\nOnly approved reviewers may open the archive."
        ),
    )

    assert response.status_code == 200
    topics = {item["topic"] for item in response.json()["missing_topics"]}
    assert "retention" in topics
    assert "incidents" in topics


def test_ask_unrelated_question_abstains(seeded_client):
    document = seeded_client.get("/api/documents").json()[0]
    response = seeded_client.post(
        "/api/ask",
        json={
            "document_id": document["id"],
            "user_id": "demo-user",
            "prompt": "What is the capital city of Mars?",
        },
    )

    assert response.status_code == 200
    assert (
        "I could not find enough support for that answer in the document."
        in response.json()["generated_text"]
    )


def test_real_use_validation_runner_outputs_report(client, tmp_path):
    repo_root = Path(__file__).resolve().parents[2]
    results_path = tmp_path / "results.json"
    report_path = tmp_path / "report.md"

    payload = run_validation(
        validation_dir=repo_root / "demo-data" / "real-use-validation",
        results_path=results_path,
        report_path=report_path,
    )

    assert payload["summary"]["total_cases"] >= 12
    assert payload["summary"]["verdict"] in {"A", "B", "C"}
    assert results_path.exists()
    assert report_path.exists()
    assert "# S TrustLoop Real-Use Validation Report" in report_path.read_text(encoding="utf-8")
