from typing import Protocol

from domain.Auth.auth import Auth
from domain.Auth.provider import Provider
from domain.error.domain_error import InvalidPasswordError, InvalidProviderError


class AuthStrategy(Protocol):
    def register(self, email: str, secret: str | None = None) -> Auth: ...
    def verify(self, auth: Auth, secret: str | None = None) -> bool: ...


class CredentialsStrategy:
    def register(self, email: str, secret: str | None = None) -> Auth:
        if not secret:
            raise InvalidPasswordError("Password is required")
        return Auth.create(email, secret)

    def verify(self, auth: Auth, secret: str | None = None) -> bool:
        if secret is None:
            return False
        return auth.verify_password(secret)


class OAuthStrategy:
    def __init__(self, provider: Provider) -> None:
        if provider.is_credentials():
            raise InvalidProviderError("OAuth provider required")
        self._provider = provider

    def register(self, email: str, secret: str | None = None) -> Auth:
        return Auth.create_from_oauth(email, self._provider)

    def verify(self, auth: Auth, secret: str | None = None) -> bool:
        return auth.provider == self._provider


def strategy_for(provider: Provider) -> AuthStrategy:
    if provider.is_credentials():
        return CredentialsStrategy()
    return OAuthStrategy(provider)
