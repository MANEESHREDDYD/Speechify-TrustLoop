from app.services.topic_extractor import detect_missing_topics


def test_evaluate_supported_claim(seeded_client):
    outputs = seeded_client.get("/api/outputs").json()
    generated = next(item for item in outputs if item["generation_mode"] == "deterministic" and item["output_type"] == "summary")
    card = seeded_client.get(f"/api/outputs/{generated['id']}/trust-card").json()
    assert card["supported_claims"] + card["weakly_supported_claims"] > 0
    assert card["trust_score"] >= 60


def test_evaluate_unsupported_claim(seeded_client):
    outputs = seeded_client.get("/api/outputs").json()
    bad = next(item for item in outputs if item["generation_mode"] == "negative_test" and item["output_type"] == "summary")
    card = seeded_client.get(f"/api/outputs/{bad['id']}/trust-card").json()
    assert card["unsupported_claims"] + card["contradicted_claims"] >= 1
    assert card["hallucination_risk"] >= 0.5


def test_wrong_meeting_notes_low_score(seeded_client):
    outputs = seeded_client.get("/api/outputs").json()
    bad = next(item for item in outputs if item["generation_mode"] == "negative_test" and item["output_type"] == "meeting_notes")
    card = seeded_client.get(f"/api/outputs/{bad['id']}/trust-card").json()
    assert card["trust_score"] < 60
    assert card["contradicted_claims"] >= 2


def test_missing_topic_detector():
    source = """
    Section 1: Benefits
    Podcasts explain dense material.
    Section 2: Limitations
    Podcasts can oversimplify technical details.
    Section 3: Privacy
    Learner data requires protection.
    """
    output = "# Podcast\nPodcasts make material easier to consume."
    missing = {item["topic"] for item in detect_missing_topics(source, output)}
    assert "limitations" in missing
    assert "privacy" in missing

