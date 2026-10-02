from fastapi import FastAPI, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

_AUTH_ID_STATE = "auth_id"


def set_rate_limit_auth_id(request: Request, auth_id: str) -> None:
    setattr(request.state, _AUTH_ID_STATE, auth_id)


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        ip = forwarded.split(",")[0].strip()
        if ip:
            return ip
    return get_remote_address(request)


def _rate_limit_key(request: Request) -> str:
    auth_id = getattr(request.state, _AUTH_ID_STATE, None)
    if isinstance(auth_id, str) and auth_id:
        return f"user:{auth_id}"
    return f"ip:{_client_ip(request)}"


limiter = Limiter(key_func=_rate_limit_key, headers_enabled=False)


def register_rate_limit(app: FastAPI) -> None:
    app.state.limiter = limiter
