from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from core.auth.application.application_error import (
    AuthAlreadyExistsError,
    EmailAlreadyExistsError,
    InvalidAuthCredentialsError,
    InvalidAuthProviderError,
)
from core.shared.application.application_error import ApplicationError
from core.shared.domain.domain_error import DomainError
from core.shared.infrastructure.infrastructure_error import InfrastructureError


def register_error_handlers(app: FastAPI) -> None:

    @app.exception_handler(ApplicationError)
    async def handle_application_error(
        _request: Request,
        exc: ApplicationError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=_status_for(exc),
            content={"detail": str(exc)},
        )

    @app.exception_handler(DomainError)
    async def handle_domain_error(
        _request: Request,
        exc: DomainError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=400,
            content={"detail": str(exc)},
        )

    @app.exception_handler(InfrastructureError)
    async def handle_infrastructure_error(
        _request: Request,
        exc: InfrastructureError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=500,
            content={"detail": str(exc)},
        )


def _status_for(exc: ApplicationError) -> int:
    if isinstance(exc, (EmailAlreadyExistsError, AuthAlreadyExistsError)):
        return 409
    if isinstance(exc, InvalidAuthCredentialsError):
        return 401
    if isinstance(exc, InvalidAuthProviderError):
        return 400
    return 400
