from io import BytesIO

from app.services.chunker import chunk_document


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "s-trustloop-backend"}


def test_seed_demo_data(client):
    response = client.post("/api/demo/seed")
    assert response.status_code == 200
    assert response.json()["documents_count"] == 10
    assert len(client.get("/api/documents").json()) == 10


def test_upload_txt_document(client):
    response = client.post(
        "/api/documents/upload",
        files={"file": ("local.txt", BytesIO(b"Title: Local Trust Note\n\nPrivacy reviews are required before launch."), "text/plain")},
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Local Trust Note"
    assert response.json()["chunks_count"] >= 1


def test_chunk_document():
    text = "Section 1: Grounding\n\nClaims need evidence.\n\nSection 2: Coverage\n\nImportant topics should not disappear."
    chunks = chunk_document(text, max_chars=60, overlap=10)
    assert len(chunks) >= 2
    assert chunks[0]["section_title"].lower().startswith("section 1")
