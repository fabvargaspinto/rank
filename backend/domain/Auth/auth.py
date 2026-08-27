from dataclasses import dataclass

from domain.Auth.auth_created_at import AuthCreatedAt
from domain.Auth.auth_email import Email
from domain.Auth.auth_id import AuthId
from domain.Auth.auth_provider import Provider
from domain.Auth.auth_last_login import AuthLastLoginAt
from domain.error.domain_error import InvalidPasswordError, InvalidProviderError
from domain.User.user_id import UserId


@dataclass(frozen=True)
class Auth:
    id: AuthId
    user_id: UserId
    email: Email
    provider: Provider
    created_at: AuthCreatedAt
    last_login_at: AuthLastLoginAt | None = None
    provider_id: str | None = None
 

    def __post_init__(self) -> None:
        if self.provider.is_credentials() and self.hashed_password is None:
            raise InvalidPasswordError("Password is required")
        if not self.provider.is_credentials() and self.hashed_password is not None:
            raise InvalidProviderError("OAuth accounts cannot have a password")
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
    
    def update_last_login_at(self) -> None:
        self.last_login_at = AuthLastLoginAt.generate()

    def __str__(self) -> str:
        return f"Auth(email={self.email}, provider={self.provider})"
