def test_demo_seed_status(client):
    assert client.get("/api/demo/status").json()["seeded"] is False
    client.post("/api/demo/seed")
    status = client.get("/api/demo/status").json()
    assert status["seeded"] is True
    assert status["documents_count"] == 10

