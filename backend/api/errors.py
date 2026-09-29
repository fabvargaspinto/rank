import logging
import re

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded

from api.request_id import REQUEST_ID_HEADER, get_request_id
from core.shared.application.application_error import ApplicationError
from core.shared.domain.domain_error import DomainError
from core.shared.infrastructure.infrastructure_error import InfrastructureError

logger = logging.getLogger("ig.errors")

_APPLICATION_STATUS = {
    "EmailAlreadyExistsError": 409,
    "AuthAlreadyExistsError": 409,
    "InvalidAuthCredentialsError": 401,
    "UserNotFoundError": 404,
    "CommentNotFoundError": 404,
    "InvalidAvatarFileError": 400,
    "UnsupportedAuthProviderError": 400,
}

_DOMAIN_STATUS = {
    "IdentityAlreadyExistsError": 409,
    "UsernameAlreadyTakenError": 409,
    "UserProfileNotFoundError": 404,
}

_VALIDATION_MESSAGES = {
    "missing": "Este campo es obligatorio",
    "extra_forbidden": "Este campo no está permitido",
    "int_parsing": "El valor tiene que ser un número",
    "greater_than_equal": "El valor es demasiado chico",
    "less_than_equal": "El valor es demasiado grande",
    "string_type": "El valor tiene que ser texto",
}

_LOC_SKIP = frozenset({"body", "query", "path", "header"})


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(ApplicationError)
    async def handle_application_error(
        request: Request,
        exc: ApplicationError,
    ) -> JSONResponse:
        status_code = _APPLICATION_STATUS.get(type(exc).__name__, 400)
        _log_error(request, exc, status_code)
        return _json_error(request, status_code, str(exc), exc)

    @app.exception_handler(DomainError)
    async def handle_domain_error(
        request: Request,
        exc: DomainError,
    ) -> JSONResponse:
        status_code = _DOMAIN_STATUS.get(type(exc).__name__, 400)
        _log_error(request, exc, status_code)
        return _json_error(request, status_code, str(exc), exc)

    @app.exception_handler(InfrastructureError)
    async def handle_infrastructure_error(
        request: Request,
        exc: InfrastructureError,
    ) -> JSONResponse:
        _log_error(request, exc, 500, traceback=True)
        return _json_error(request, 500, str(exc), exc)

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        detail, field, code = _validation_error(exc)
        _log_error(request, exc, 422)
        return _json_error(
            request,
            422,
            detail,
            code=code,
            field=field,
        )

    @app.exception_handler(RateLimitExceeded)
    async def handle_rate_limit(
        request: Request,
        exc: RateLimitExceeded,
    ) -> JSONResponse:
        _log_error(request, exc, 429)
        return _json_error(
            request,
            429,
            "Demasiadas solicitudes. Probá de nuevo en un rato.",
            code="RATE_LIMITED",
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_error(
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        _log_error(request, exc, 500, traceback=True)
        return _json_error(
            request,
            500,
            "Error interno",
            code="INTERNAL_ERROR",
        )


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


def _json_error(
    request: Request,
    status_code: int,
    detail: str,
    exc: Exception | None = None,
    *,
    code: str | None = None,
    field: str | None = None,
) -> JSONResponse:
    resolved_code = code or (_code_for(exc) if exc is not None else "INTERNAL_ERROR")
    resolved_field = field if field is not None else _field_for(exc)
    request_id = get_request_id(request)
    content: dict[str, str] = {
        "code": resolved_code,
        "detail": detail,
        "request_id": request_id,
    }
    if resolved_field:
        content["field"] = resolved_field

    response = JSONResponse(status_code=status_code, content=content)
    if request_id != "-":
        response.headers[REQUEST_ID_HEADER] = request_id
    return response


def _code_for(exc: Exception) -> str:
    explicit = getattr(exc, "code", None)
    if isinstance(explicit, str) and explicit:
        return explicit
    name = type(exc).__name__.removesuffix("Error")
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).upper()


def _field_for(exc: Exception | None) -> str | None:
    if exc is None:
        return None
    field = getattr(exc, "field", None)
    return field if isinstance(field, str) and field else None


def _validation_error(exc: RequestValidationError) -> tuple[str, str | None, str]:
    errors = exc.errors()
    if not errors:
        return "El valor no es válido", None, "VALIDATION_ERROR"

    error = errors[0]
    loc = [
        part
        for part in error.get("loc", ())
        if isinstance(part, str) and part not in _LOC_SKIP
    ]
    field = loc[-1] if loc else None
    kind = str(error.get("type", ""))
    if kind in {"uuid_parsing", "uuid_type"}:
        return "El id no es válido", field, "INVALID_ID"
    return (
        _VALIDATION_MESSAGES.get(kind, "El valor no es válido"),
        field,
        "VALIDATION_ERROR",
    )
