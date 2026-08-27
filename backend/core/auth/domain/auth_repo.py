from dataclasses import dataclass
from typing import Protocol

from core.auth.domain.auth import Auth
from core.auth.domain.auth_email import Email
from core.auth.domain.auth_password import Password


@dataclass(frozen=True)
class RegisterAuthResult:
    auth: Auth
    access_token: str | None = None
    refresh_token: str | None = None
    expires_in: int | None = None


class AuthRepo(Protocol):
    def register(self, email: Email, password: Password) -> RegisterAuthResult: ...
