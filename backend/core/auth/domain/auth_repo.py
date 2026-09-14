from dataclasses import dataclass
from typing import Protocol

from core.auth.domain.auth import Auth
from core.auth.domain.auth_error import IdentityAlreadyExistsError
from core.auth.domain.auth_provider import AuthProvider
from core.user.domain.user import User

__all__ = [
    "AuthIdentity",
    "AuthRepository",
    "IdentityAlreadyExistsError",
]


@dataclass(frozen=True)
class AuthIdentity:
    id: str
    provider: AuthProvider
    provider_id: str | None
    email: str | None


class AuthRepository(Protocol):

    def save(self, user: User, auth: Auth) -> Auth:
        """Persist user and auth.

        Raises:
            IdentityAlreadyExistsError: unique identity conflict (email or provider).
        """

    def find_by_id(self, auth_id: str) -> Auth | None:
        pass

    def find_by_email(self, email: str) -> Auth | None:
        pass

    def find_by_provider_id(
        self, provider: AuthProvider, provider_id: str
    ) -> Auth | None:
        pass

    def get_identity(self, auth_id: str) -> AuthIdentity | None:
        pass
