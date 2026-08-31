from dataclasses import dataclass
from typing import Protocol

from core.auth.domain.auth import Auth


@dataclass(frozen=True)
class RegisterCredentialsAuthResult:
    auth: Auth
    access_token: str | None = None
    refresh_token: str | None = None
    expires_in: int | None = None


class AuthRepo(Protocol):
    def register(self, email: str, password: str, provider: str, name: str) -> None: ...
