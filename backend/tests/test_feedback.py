def test_feedback_saved(seeded_client):
    output = seeded_client.get("/api/outputs").json()[0]
    response = seeded_client.post("/api/feedback", json={
        "user_id": "demo-user",
        "output_id": output["id"],
        "feedback_type": "missing_key_point",
        "comment": "The output skipped privacy.",
    })
    assert response.status_code == 200
    summary = seeded_client.get("/api/feedback/summary").json()
    assert summary["distribution"]["missing_key_point"] == 1

