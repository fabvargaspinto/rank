from fastapi.testclient import TestClient

from main import app


def test_health_returns_200_when_fastapi_is_up():
    response = TestClient(app).get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_health_does_not_require_authorization():
    response = TestClient(app).get("/health")

    assert "Authorization" not in response.request.headers
    assert response.status_code == 200
