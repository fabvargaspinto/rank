import hashlib

from fastapi import FastAPI, Request
from slowapi import Limiter
from slowapi.util import get_remote_address


def _authenticated_user_key(request: Request) -> str:
    header = request.headers.get("authorization", "")
    prefix = "bearer "
    if header.lower().startswith(prefix):
        token = header[len(prefix) :].strip()
        if token:
            return hashlib.sha256(token.encode()).hexdigest()
    return get_remote_address(request)


limiter = Limiter(key_func=_authenticated_user_key, headers_enabled=False)


def register_rate_limit(app: FastAPI) -> None:
    app.state.limiter = limiter
