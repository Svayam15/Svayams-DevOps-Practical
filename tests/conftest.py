import pytest

from app import create_app


@pytest.fixture
def client(tmp_path):
    app = create_app({"TESTING": True, "DATABASE": str(tmp_path / "test.db")})
    return app.test_client()


@pytest.fixture
def sample(client):
    r = client.post(
        "/api/students", json={"name": "Asha Rao", "email": "asha@example.com", "course": "MSc IT"}
    )
    return r.get_json()
