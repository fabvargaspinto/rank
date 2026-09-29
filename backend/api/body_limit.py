from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

from api.request_id import REQUEST_ID_HEADER, get_request_id

MAX_REQUEST_BYTES = 3 * 1024 * 1024


def register_body_limit(app: FastAPI) -> None:
    app.add_middleware(BodySizeLimitMiddleware)


class BodySizeLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        raw_length = request.headers.get("content-length")
        if raw_length is not None and raw_length.isdigit():
            if int(raw_length) > MAX_REQUEST_BYTES:
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
        return await call_next(request)
