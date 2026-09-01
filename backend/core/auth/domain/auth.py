from dataclasses import dataclass

from core.auth.domain.auth_created_at import AuthCreatedAt
from core.auth.domain.auth_email import Email
from core.auth.domain.auth_id import AuthId
from core.auth.domain.auth_provider import Provider
from core.auth.domain.auth_last_login import AuthLastLoginAt
from core.auth.domain.auth_error import InvalidProviderError
from core.auth.domain.auth_password import AuthPassword
from core.user.domain.user_id import UserId


@dataclass(frozen=True)
class   Auth:
    id: AuthId
    user_id: UserId
    email: Email
    provider: Provider
    created_at: AuthCreatedAt
    last_login_at: AuthLastLoginAt | None = None
    provider_id: str | None = None

    def __post_init__(self) -> None:
        if self.provider.is_credentials() and self.provider_id:
            raise InvalidProviderError("Credentials accounts cannot have a provider id")
        if not self.provider.is_credentials() and not self.provider_id:
            raise InvalidProviderError("OAuth provider id is required")

    @classmethod
    def create_with_credentials(cls, user_id: UserId, email: str) -> "Auth":
        return cls(
            id=AuthId.generate(),
            user_id=user_id,
            email=Email(email),
            provider=Provider.from_credentials(),
            created_at=AuthCreatedAt.generate(),
        )

    @classmethod
    def create_from_oauth(
        cls,
        user_id: UserId,
        email: str,
        provider: Provider,
        provider_id: str,
    ) -> "Auth":
        if provider.is_credentials():
            raise InvalidProviderError("OAuth provider required")
        return cls(
            id=AuthId.generate(),
            user_id=user_id,
            email=Email(email),
            provider=provider,
            provider_id=provider_id,
            created_at=AuthCreatedAt.generate(),
        )

    @classmethod
    def validate_password(cls, password: str) -> None:
        AuthPassword.validate(password)

    def update_last_login_at(self) -> None:
        self.last_login_at = AuthLastLoginAt.generate()

    def to_primitives(self):
        return {
            "id": self.id.value,
            "user_id": self.user_id.value,
            "email": self.email.value,
            "provider": self.provider.value,
            "created_at": self.created_at.value,
            "last_login_at": self.last_login_at.value if self.last_login_at else None,
            "provider_id": self.provider_id
        }
    @classmethod
    def from_primitives(cls,
        id: str,
        user_id: str,
        email: str,
        provider: str,
        created_at: str,
        last_login_at: str | None,
        provider_id: str | None
    ) -> "Auth":
        return cls(
            id=AuthId(id),
            user_id=UserId(user_id),
            email=Email(email),
            provider=Provider(provider),
            created_at=AuthCreatedAt(created_at),
            last_login_at=AuthLastLoginAt(last_login_at) if last_login_at else None,
            provider_id=provider_id
        )

    def __str__(self) -> str:
        return f"Auth(email={self.email}, provider={self.provider})"
