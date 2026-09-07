from dataclasses import dataclass
from typing import Protocol

from core.auth.domain.auth import Auth
from core.user.domain.user import User


@dataclass(frozen=True)
class AuthSession:
    access_token: str
    refresh_token: str
    expires_in: int


@dataclass(frozen=True)
class RegisterAuthResult:
    auth: Auth
    session: AuthSession | None = None


@dataclass(frozen=True)
class RegisterCredentialsAuthResult:
    auth: Auth
    access_token: str | None = None
    refresh_token: str | None = None
    expires_in: int | None = None


class AuthRepo(Protocol):
    def register(
        self,
        auth: Auth,
        user: User,
        password: str | None = None,
    ) -> None: ...

    def login(self, email: str, password: str) -> AuthSession: ...
