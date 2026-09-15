from uuid import UUID

from fastapi.testclient import TestClient

from controller.request_id import REQUEST_ID_HEADER
from main import app


def test_echoes_incoming_request_id():
    response = TestClient(app).get(
        "/health",
        headers={REQUEST_ID_HEADER: "from-next-123"},
    )

    assert response.status_code == 200
    assert response.headers[REQUEST_ID_HEADER] == "from-next-123"


def test_generates_request_id_when_missing():
    response = TestClient(app).get("/health")

    UUID(response.headers[REQUEST_ID_HEADER])


def test_error_response_propagates_request_id():
    response = TestClient(app).post(
        "/auth/session",
        headers={REQUEST_ID_HEADER: "session-error-1"},
    )

    assert response.status_code == 401
    assert response.json() == {
        "detail": "El token de autenticación no es válido"
    }
    assert response.headers[REQUEST_ID_HEADER] == "session-error-1"
