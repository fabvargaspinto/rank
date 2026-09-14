from core.auth.application.application_error import (
    EmailAlreadyExistsError,
    InvalidAuthCredentialsError,
    InvalidAuthProviderError,
)
from core.auth.domain.auth import Auth
from core.auth.domain.auth_email import AuthEmail
from core.auth.domain.auth_provider import AuthProvider
from core.auth.domain.auth_repo import AuthRepository
from core.user.domain.user import User


class ProvisionOAuthUser:
    def __init__(self, auth_repo: AuthRepository):
        self.auth_repo = auth_repo

    def execute(
        self,
        auth_id: str,
        email: str,
        provider: AuthProvider,
        provider_id: str | None,
    ) -> Auth:
        if not email.strip():
            raise InvalidAuthCredentialsError(
                "El email es requerido"
            )

        if not provider.is_oauth():
            raise InvalidAuthProviderError(
                "El proveedor debe ser un proveedor OAuth"
            )

        if not provider_id:
            raise InvalidAuthCredentialsError(
                "El token de autenticación no es válido"
            )

        existing = self.auth_repo.find_by_id(auth_id)
        if existing:
            return existing

        existing_by_provider = self.auth_repo.find_by_provider_id(
            provider,
            provider_id,
        )
        if existing_by_provider:
            return existing_by_provider

        email_vo = AuthEmail(email)
        if self.auth_repo.find_by_email(email_vo.value):
            raise EmailAlreadyExistsError(
                "El email ya está registrado"
            )

        user = User.create_empty()
        auth = Auth.create_with_oauth(
            id=auth_id,
            user_id=user.id.value,
            provider=provider,
            provider_id=provider_id,
            email=email_vo.value,
        )

        return self.auth_repo.save(user=user, auth=auth)
