from core.auth.application.application_error import InvalidAuthCredentialsError
from core.auth.application.provision_oauth_user import ProvisionOAuthUser
from core.auth.application.register_with_email import RegisterWithEmail
from core.auth.domain.auth import Auth
from core.auth.domain.auth_repo import AuthRepository


class EnsureUserProvisioned:
    def __init__(
        self,
        auth_repo: AuthRepository,
        register_with_email: RegisterWithEmail | None = None,
        provision_oauth_user: ProvisionOAuthUser | None = None,
    ):
        self.auth_repo = auth_repo
        self.register_with_email = register_with_email or RegisterWithEmail(
            auth_repo
        )
        self.provision_oauth_user = provision_oauth_user or ProvisionOAuthUser(
            auth_repo
        )

    def execute(self, auth_id: str, email: str) -> Auth:
        if not email.strip():
            raise InvalidAuthCredentialsError(
                "El email es requerido"
            )

        existing = self.auth_repo.find_by_id(auth_id)
        if existing:
            return existing

        identity = self.auth_repo.get_identity(auth_id)
        if not identity:
            raise InvalidAuthCredentialsError(
                "El token de autenticación no es válido"
            )

        if identity.provider.is_email():
            return self.register_with_email.execute(auth_id, email)

        return self.provision_oauth_user.execute(
            auth_id,
            email,
            identity.provider,
            identity.provider_id,
        )
