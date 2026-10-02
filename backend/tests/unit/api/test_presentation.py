import asyncio
import json
import logging

from fastapi.testclient import TestClient
from starlette.requests import Request

from api.body_limit import MAX_REQUEST_BYTES, BodySizeLimitMiddleware
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


def test_rejects_a_chunked_body_over_three_megabytes():
    """Sin Content-Length (p. ej. Transfer-Encoding: chunked) también se limita."""
    chunk = b"x" * (64 * 1024)
    chunk_count = (MAX_REQUEST_BYTES // len(chunk)) + 2
    sent = {"i": 0}

    async def receive() -> dict:
        i = sent["i"]
        if i < chunk_count:
            sent["i"] = i + 1
            return {"type": "http.request", "body": chunk, "more_body": True}
        return {"type": "http.request", "body": b"", "more_body": False}

    scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": "POST",
        "scheme": "http",
        "path": "/auth/session",
        "raw_path": b"/auth/session",
        "query_string": b"",
        "headers": [
            (b"content-type", b"application/octet-stream"),
            (b"transfer-encoding", b"chunked"),
        ],
        "client": ("testclient", 50000),
        "server": ("testserver", 80),
    }

    async def run() -> None:
        middleware = BodySizeLimitMiddleware(create_app())

        async def call_next(_request):  # pragma: no cover
            raise AssertionError("no debería llegar al endpoint")

        response = await middleware.dispatch(Request(scope, receive), call_next)
        assert response.status_code == 413
        assert json.loads(response.body)["code"] == "PAYLOAD_TOO_LARGE"

    asyncio.run(run())


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
