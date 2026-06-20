def test_learning_memory_updates(seeded_client):
    response = seeded_client.post("/api/learning-memory/recompute", json={"user_id": "demo-user"})
    assert response.status_code == 200
    memory = response.json()
    assert memory["documents_studied"] == 10
    assert memory["strong_topics"] or memory["weak_topics"]
    assert memory["recommended_recap"]


def test_analytics_overview(seeded_client):
    overview = seeded_client.get("/api/analytics/overview").json()
    assert overview["documents_count"] == 10
    assert overview["outputs_count"] == 6
    assert overview["evaluations_count"] == 6
    assert overview["average_trust_score"] > 0

