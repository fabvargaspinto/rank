from core.auth.domain.auth import Auth
from core.auth.domain.auth_provider import AuthProvider
from core.auth.domain.auth_repo import (
    AuthIdentity,
    AuthRepository,
    IdentityAlreadyExistsError,
)
from core.user.domain.user import User


class FakeAuthRepo(AuthRepository):
    def __init__(self):
        self.auths: list[Auth] = []
        self.users: list[User] = []
        self.identity: AuthIdentity | None = None
        self.fail_on_save = False

    def save(self, user: User, auth: Auth) -> Auth:
        if self.fail_on_save or self._conflicts(auth):
            raise IdentityAlreadyExistsError("La identidad ya existe")

        self.users.append(user)
        self.auths.append(auth)
        return auth

    def find_by_id(self, auth_id: str) -> Auth | None:
        for auth in self.auths:
            if auth.id.value == auth_id:
                return auth
        return None

    def find_by_email(self, email: str) -> Auth | None:
        for auth in self.auths:
            if auth.email is not None and auth.email.value == email:
                return auth
        return None

    def find_by_provider_id(
        self, provider: AuthProvider, provider_id: str
    ) -> Auth | None:
        for auth in self.auths:
            method = auth.provider_method
            if (
                method.provider == provider
                and method.provider_id is not None
                and method.provider_id.value == provider_id
            ):
                return auth
        return None

    def get_identity(self, auth_id: str) -> AuthIdentity | None:
        if self.identity is not None and self.identity.id == auth_id:
            return self.identity
        return None

    def _conflicts(self, auth: Auth) -> bool:
        for existing in self.auths:
            if existing.id.value == auth.id.value:
                return True

            if (
                auth.email is not None
                and existing.email is not None
                and existing.email.value == auth.email.value
            ):
                return True

            existing_provider_id = existing.provider_method.provider_id
            new_provider_id = auth.provider_method.provider_id
            if (
                existing_provider_id is not None
                and new_provider_id is not None
                and existing.provider_method.provider == auth.provider_method.provider
                and existing_provider_id.value == new_provider_id.value
            ):
                return True

        return False
