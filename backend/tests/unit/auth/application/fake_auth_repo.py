from uuid import uuid4

from core.auth.domain.auth import Auth
from core.auth.domain.auth_provider import AuthProvider
from core.auth.domain.auth_repo import AuthRepository, OAuthIdentity
from core.auth.infrastructure.error_infrastructure import IdentityAlreadyExistsError
from core.user.domain.user import User


class FakeAuthRepo(AuthRepository):
    def __init__(self):
        self.auths = []
        self.users = []
        self.identities = {}
        self.oauth_identity: OAuthIdentity | None = None

    def save(self, user: User, auth: Auth) -> Auth:
        self.users.append(user)
        self.auths.append(auth)
        return auth

    def create_identity(self, email: str, password: str) -> str:
        for data in self.identities.values():
            if data["email"] == email:
                raise IdentityAlreadyExistsError(
                    "El email ya está registrado"
                )

        auth_id = str(uuid4())
        self.identities[auth_id] = {
            "email": email,
            "password": password,
        }
        return auth_id

    def delete_identity(self, auth_id: str) -> None:
        self.identities.pop(auth_id, None)

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

    def get_oauth_identity(self, access_token: str) -> OAuthIdentity | None:
        return self.oauth_identity

    def verify_password(self, email: str, password: str) -> bool:
        for data in self.identities.values():
            if data["email"] == email:
                return data["password"] == password
        return False
