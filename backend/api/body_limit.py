from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

from api.request_id import REQUEST_ID_HEADER, get_request_id

MAX_REQUEST_BYTES = 3 * 1024 * 1024
_METHODS_WITH_BODY = frozenset({"POST", "PUT", "PATCH"})


def register_body_limit(app: FastAPI) -> None:
    app.add_middleware(BodySizeLimitMiddleware)


def _payload_too_large(request: Request) -> JSONResponse:
    request_id = get_request_id(request)
    response = JSONResponse(
        status_code=413,
        content={
            "code": "PAYLOAD_TOO_LARGE",
            "detail": "La solicitud es demasiado grande",
            "request_id": request_id,
        },
    )
    if request_id != "-":
        response.headers[REQUEST_ID_HEADER] = request_id
    return response


class BodySizeLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        raw_length = request.headers.get("content-length")
        if raw_length is not None:
            if not raw_length.isdigit() or int(raw_length) > MAX_REQUEST_BYTES:
                return _payload_too_large(request)
            return await call_next(request)

        if request.method not in _METHODS_WITH_BODY:
            return await call_next(request)

        body = bytearray()
        async for chunk in request.stream():
            body.extend(chunk)
            if len(body) > MAX_REQUEST_BYTES:
                return _payload_too_large(request)

        async def receive() -> dict:
            return {"type": "http.request", "body": bytes(body), "more_body": False}

        return await call_next(Request(request.scope, receive))
