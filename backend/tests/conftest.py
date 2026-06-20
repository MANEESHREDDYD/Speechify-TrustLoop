import os
import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


_TEST_DATABASE_DIRECTORY = tempfile.TemporaryDirectory(prefix="s-trustloop-tests-")
_TEST_DATABASE_PATH = Path(_TEST_DATABASE_DIRECTORY.name) / "test-s-trustloop.db"
os.environ["DATABASE_URL"] = f"sqlite:///{_TEST_DATABASE_PATH.as_posix()}"


from app.database import SessionLocal, engine, init_db
from app.main import app
from app.services.seed_data import reset_demo


@pytest.fixture(scope="session", autouse=True)
def isolated_test_database():
    init_db()
    yield
    engine.dispose()
    _TEST_DATABASE_DIRECTORY.cleanup()


@pytest.fixture(scope="session")
def test_database_path():
    return _TEST_DATABASE_PATH


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
