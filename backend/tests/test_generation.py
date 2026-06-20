def first_document(client, title):
    return next(item for item in client.get("/api/documents").json() if item["title"] == title)


def generate(client, path, document_id):
    return client.post(path, json={"document_id": document_id, "user_id": "demo-user", "mode": "deterministic"})


def test_generate_summary(seeded_client):
    document = first_document(seeded_client, "Voice AI and Accessible Learning")
    response = generate(seeded_client, "/api/generate/summary", document["id"])
    assert response.status_code == 200
    assert "# Summary" in response.json()["generated_text"]
    assert "reading fatigue" in response.json()["generated_text"].lower()


def test_generate_quiz(seeded_client):
    document = first_document(seeded_client, "Voice AI and Accessible Learning")
    response = generate(seeded_client, "/api/generate/quiz", document["id"])
    text = response.json()["generated_text"]
    assert "# Quiz" in text
    assert "Answer: B" in text
    assert "Source topic:" in text


def test_generate_meeting_notes(seeded_client):
    document = first_document(seeded_client, "Voice AI Meeting Notes Product Launch")
    response = generate(seeded_client, "/api/generate/meeting-notes", document["id"])
    text = response.json()["generated_text"]
    assert "July 15" in text
    assert "| Priya |" in text
    assert "Privacy review is required" in text

