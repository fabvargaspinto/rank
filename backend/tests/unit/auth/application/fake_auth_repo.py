from core.auth.domain.auth import Auth
from core.auth.domain.auth_provider import AuthProvider
from core.auth.domain.auth_repo import AuthIdentity, AuthRepository
from core.user.domain.user import User


class FakeAuthRepo(AuthRepository):
    def __init__(self):
        self.auths = []
        self.users = []
        self.identity: AuthIdentity | None = None

    def save(self, user: User, auth: Auth) -> Auth:
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

    def get_identity(self, access_token: str) -> AuthIdentity | None:
        return self.identity
