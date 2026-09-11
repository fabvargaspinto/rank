from typing import Protocol

from core.auth.domain.auth import Auth
from core.auth.domain.auth_id import AuthId
from core.auth.domain.auth_method import AuthMethod
from core.auth.domain.auth_provider import AuthProvider
from core.user.domain.user import User


class AuthRepository(Protocol):
    def create_user(
        self,
        user: User,
        auth: Auth,
        method: AuthMethod,
        password: str | None = None,
    ) -> None:
        pass

    def link_auth_provider(
        self,
        auth: Auth,
        method: AuthMethod,
        password: str | None = None,
    ) -> None:
        pass

    def find_auth_by_email(self, email: str) -> Auth | None:
        pass

    def auth_has_provider(self, auth_id: AuthId, provider: AuthProvider) -> bool:
        pass

    def find_auth_method(
        self, auth_id: AuthId, provider: AuthProvider
    ) -> AuthMethod | None:
        pass

    def login_with_email(self, email: str, password: str) -> tuple[str, str]:
        pass

    def login_with_oauth(self, email: str) -> tuple[str, str]:
        pass
