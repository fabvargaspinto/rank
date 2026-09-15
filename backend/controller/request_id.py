from uuid import uuid4

from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

REQUEST_ID_HEADER = "X-Request-ID"
_MAX_REQUEST_ID_LENGTH = 128


def get_request_id(request: Request) -> str:
    request_id = getattr(request.state, "request_id", None)
    if isinstance(request_id, str) and request_id:
        return request_id
    return _parse_request_id(request.headers.get(REQUEST_ID_HEADER)) or "-"


def register_request_id(app: FastAPI) -> None:
    app.add_middleware(RequestIdMiddleware)


class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        request_id = (
            _parse_request_id(request.headers.get(REQUEST_ID_HEADER))
            or str(uuid4())
        )
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers[REQUEST_ID_HEADER] = request_id
        return response


def _parse_request_id(value: str | None) -> str | None:
    if value is None:
        return None
    request_id = value.strip()
    if not request_id or len(request_id) > _MAX_REQUEST_ID_LENGTH:
        return None
    if not all(char.isalnum() or char in ".-_" for char in request_id):
        return None
    return request_id
