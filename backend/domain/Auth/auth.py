from dataclasses import dataclass, field
from datetime import datetime

from domain.Auth.email import Email
from domain.Auth.hash_password import HashPassword
from domain.Auth.provider import Provider
from domain.error.domain_error import InvalidPasswordError, InvalidProviderError


@dataclass(frozen=True)
class Auth:
    email: Email
    provider: Provider
    provider_id: str | None = None
    hashed_password: HashPassword | None = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

  
    @classmethod
    def create(cls, email: str, password: str) -> "Auth":
        return cls(
            email=Email(email),
            provider=Provider.from_credentials(),
            hashed_password=HashPassword.from_plain(password),
        )

    @classmethod
    def create_from_oauth(cls, email: str, provider: Provider, provider_id: str) -> "Auth":
        if provider.is_credentials():
            raise InvalidProviderError("OAuth provider required")
        return cls(email=Email(email), provider=provider, provider_id=provider_id)

    def verify_password(self, password: str) -> bool:
        if self.hashed_password is None:
            return False
        return self.hashed_password.verify(password)

    def __str__(self) -> str:
        return f"Auth(email={self.email}, provider={self.provider})"
