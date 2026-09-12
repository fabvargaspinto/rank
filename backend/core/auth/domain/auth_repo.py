from dataclasses import dataclass
from typing import Protocol

from core.auth.domain.auth import Auth
from core.auth.domain.auth_provider import AuthProvider
from core.user.domain.user import User


@dataclass(frozen=True)
class OAuthIdentity:
    id: str
    provider: AuthProvider
    provider_id: str
    email: str | None


class AuthRepository(Protocol):

    def save(self, user: User, auth: Auth) -> Auth:
        pass

    def create_identity(self, email: str, password: str) -> str:
        pass

    def delete_identity(self, auth_id: str) -> None:
        pass

    def find_by_email(self, email: str) -> Auth | None:
        pass

    def find_by_provider_id(
        self, provider: AuthProvider, provider_id: str
    ) -> Auth | None:
        pass

    def get_oauth_identity(self, access_token: str) -> OAuthIdentity | None:
        pass

    def verify_password(self, email: str, password: str) -> bool:
        pass
