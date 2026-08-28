from typing import Callable, Protocol

from core.auth.domain.auth import Auth
from core.auth.domain.auth_provider import Provider
from core.auth.domain.auth_error import InvalidPasswordError, InvalidProviderError
from core.user.domain.user_id import UserId


class AuthStrategy(Protocol):
    def register(
        self,
        user_id: UserId,
        email: str,
        secret: str | None = None,
        provider_id: str | None = None,
    ) -> Auth: ...

    def verify(self, auth: Auth, secret: str | None = None) -> bool: ...


class CredentialsStrategy:
    def register(
        self,
        user_id: UserId,
        email: str,
        secret: str 
    ) -> Auth:
        if not secret:
            raise InvalidPasswordError("Password is required")
        return Auth.create_with_credentials(user_id, email, secret)

    def verify(self, auth: Auth, secret: str | None = None) -> bool:
        if secret is None:
            return False
        return auth.verify_password(secret)


class OAuthStrategy:
    def __init__(self, provider: Provider) -> None:
        if provider.is_credentials():
            raise InvalidProviderError("OAuth provider required")
        self._provider = provider

    def register(
        self,
        user_id: UserId,
        email: str,
        provider_id: str | None = None,
    ) -> Auth:
        if not provider_id:
            raise InvalidProviderError("OAuth provider id is required")
        return Auth.create_from_oauth(user_id, email, self._provider, provider_id)

    def verify(self, auth: Auth) -> bool:
        return auth.provider == self._provider


def get_strategy(provider: Provider) -> AuthStrategy:
    if provider.is_credentials():
        return CredentialsStrategy()
    return OAuthStrategy(provider)


GetStrategy = Callable[[Provider], AuthStrategy]
