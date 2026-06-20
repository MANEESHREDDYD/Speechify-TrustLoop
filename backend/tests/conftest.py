import pytest
from fastapi.testclient import TestClient

from app.database import SessionLocal, init_db
from app.main import app
from app.services.seed_data import reset_demo


@pytest.fixture
def client():
    init_db()
    with SessionLocal() as session:
        reset_demo(session)
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def seeded_client(client):
    response = client.post("/api/demo/seed")
    assert response.status_code == 200
    return client

