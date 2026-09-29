import json
import logging

from fastapi.testclient import TestClient

from api.body_limit import MAX_REQUEST_BYTES
from api.logging import HealthAccessFilter, JsonFormatter
from main import create_app


def test_production_hides_docs(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "production")

    app = create_app()

    assert app.docs_url is None
    assert app.redoc_url is None
    assert app.openapi_url is None


def test_rejects_a_body_over_three_megabytes():
    response = TestClient(create_app()).post(
        "/auth/session",
        content=b"x" * (MAX_REQUEST_BYTES + 1),
        headers={"content-type": "application/octet-stream"},
    )

    assert response.status_code == 413
    assert response.json()["code"] == "PAYLOAD_TOO_LARGE"


def test_json_formatter_keeps_extra_fields():
    record = logging.LogRecord(
        name="ig.errors",
        level=logging.WARNING,
        pathname=__file__,
        lineno=1,
        msg="handled_error",
        args=(),
        exc_info=None,
    )
    record.request_id = "req-1"
    record.status_code = 400

    payload = json.loads(JsonFormatter().format(record))

    assert payload["message"] == "handled_error"
    assert payload["request_id"] == "req-1"
    assert payload["status_code"] == 400


def test_health_access_filter_drops_healthchecks():
    record = logging.LogRecord(
        name="uvicorn.access",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg='%s - "%s %s HTTP/%s" %d',
        args=("127.0.0.1:1", "GET", "/health", "1.1", 200),
        exc_info=None,
    )
    other = logging.LogRecord(
        name="uvicorn.access",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg='%s - "%s %s HTTP/%s" %d',
        args=("127.0.0.1:1", "GET", "/me", "1.1", 200),
        exc_info=None,
    )

    access_filter = HealthAccessFilter()

    assert access_filter.filter(record) is False
    assert access_filter.filter(other) is True
