from dataclasses import dataclass

from core.auth.domain.auth_created_at import AuthCreatedAt
from core.auth.domain.auth_email import AuthEmail
from core.auth.domain.auth_error import InvalidEmailError
from core.auth.domain.auth_id import AuthId
from core.user.domain.user_id import UserId
from core.auth.domain.auth_method import AuthMethod
from core.auth.domain.auth_provider import AuthProvider


@dataclass(frozen=True)
class Auth:
    id: AuthId
    user_id: UserId
    created_at: AuthCreatedAt
    provider_method: AuthMethod
    email: AuthEmail | None = None

    def __post_init__(self) -> None:
        if self.email is None:
            raise InvalidEmailError("El email es requerido")

    @staticmethod
    def create_with_email(id: str, user_id: str, email: str) -> "Auth":
        return Auth(
            id=AuthId(id),
            user_id=UserId(user_id),
            email=AuthEmail(email),
            created_at=AuthCreatedAt.now(),
            provider_method=AuthMethod.email(),
        )

    @staticmethod
    def create_with_oauth(
        id: str,
        user_id: str,
        provider: AuthProvider,
        provider_id: str,
        email: str,
    ) -> "Auth":
        return Auth(
            id=AuthId(id),
            user_id=UserId(user_id),
            email=AuthEmail(email),
            created_at=AuthCreatedAt.now(),
            provider_method=AuthMethod.oauth(provider, provider_id),
        )
