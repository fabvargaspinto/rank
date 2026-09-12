from dataclasses import dataclass

from core.auth.domain.auth_created_at import AuthCreatedAt
from core.auth.domain.auth_email import AuthEmail
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

    @staticmethod
    def create_with_email(id:str,user_id: str, email: str) -> "Auth":
        return Auth(
            id=AuthId(id),
            user_id=UserId(user_id),
            email=AuthEmail(email),
            created_at=AuthCreatedAt.now(),
            provider_method=AuthMethod.email(),
        )

    @staticmethod
    def create_with_oauth(
        id:str,
        user_id: str,
        provider: AuthProvider,
        provider_id: str,
        email: str | None = None,
    ) -> "Auth":
        return Auth(
            id=AuthId(id),
            user_id=UserId(user_id),
            email=AuthEmail(email) if email is not None else None,
            created_at=AuthCreatedAt.now(),
            provider_method=AuthMethod.oauth(provider, provider_id),
        )

    @staticmethod
    def from_primitive(primitive: dict) -> "Auth":
        return Auth(
            id=AuthId(primitive["id"]),
            user_id=UserId(primitive["user_id"]),
            email=AuthEmail(primitive["email"]) if primitive["email"] is not None else None,
            created_at=AuthCreatedAt.from_isoformat(primitive["created_at"]),
            provider_method=AuthMethod.from_primitive(primitive["provider_method"]),
        )

    def to_primitive(self) -> dict:
        return {
            "id": self.id.value,
            "user_id": self.user_id.value,
            "email": self.email.value if self.email is not None else None,
            "created_at": self.created_at.to_isoformat(),
            "provider_method": self.provider_method.to_primitive(),
        }