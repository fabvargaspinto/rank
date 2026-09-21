import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from controller.request_id import REQUEST_ID_HEADER, get_request_id
from core.auth.application.application_error import (
    AuthAlreadyExistsError,
    EmailAlreadyExistsError,
    InvalidAuthCredentialsError,
    UnsupportedAuthProviderError,
)
from core.auth.domain.auth_error import IdentityAlreadyExistsError
from core.shared.application.application_error import ApplicationError
from core.shared.domain.domain_error import DomainError
from core.shared.infrastructure.infrastructure_error import InfrastructureError
from core.user.application.application_error import (
    UserNameAlreadyExistsError,
    UserNotFoundError,
)

logger = logging.getLogger("ig.errors")


def register_error_handlers(app: FastAPI) -> None:

    @app.exception_handler(ApplicationError)
    async def handle_application_error(
        request: Request,
        exc: ApplicationError,
    ) -> JSONResponse:
        status_code = _status_for(exc)
        _log_error(request, exc, status_code)
        return _json_error(request, status_code, str(exc))

    @app.exception_handler(DomainError)
    async def handle_domain_error(
        request: Request,
        exc: DomainError,
    ) -> JSONResponse:
        status_code = 409 if isinstance(exc, IdentityAlreadyExistsError) else 400
        _log_error(request, exc, status_code)
        return _json_error(request, status_code, str(exc))

    @app.exception_handler(InfrastructureError)
    async def handle_infrastructure_error(
        request: Request,
        exc: InfrastructureError,
    ) -> JSONResponse:
        _log_error(request, exc, 500, traceback=True)
        return _json_error(request, 500, str(exc))


def _log_error(
    request: Request,
    exc: Exception,
    status_code: int,
    *,
    traceback: bool = False,
) -> None:
    extra = {
        "path": request.url.path,
        "method": request.method,
        "status_code": status_code,
        "error_type": type(exc).__name__,
        "request_id": get_request_id(request),
    }
    if traceback:
        logger.exception("infrastructure_error", extra=extra)
        return
    logger.warning("handled_error", extra=extra)


def _json_error(request: Request, status_code: int, detail: str) -> JSONResponse:
    response = JSONResponse(
        status_code=status_code,
        content={"detail": detail},
    )
    request_id = get_request_id(request)
    if request_id != "-":
        response.headers[REQUEST_ID_HEADER] = request_id
    return response


def _status_for(exc: ApplicationError) -> int:
    if isinstance(exc, (EmailAlreadyExistsError, AuthAlreadyExistsError)):
        return 409
    if isinstance(exc, InvalidAuthCredentialsError):
        return 401
    if isinstance(exc, UserNotFoundError):
        return 404
    if isinstance(exc, UserNameAlreadyExistsError):
        return 409
    if isinstance(exc, UnsupportedAuthProviderError):
        return 400
    return 400
