from core.auth.application.application_error import (
    EmailAlreadyExistsError,
    InvalidAuthCredentialsError,
    UnsupportedAuthProviderError,
)
from core.auth.domain.auth import Auth
from core.auth.domain.auth_email import AuthEmail
from core.auth.domain.auth_provider import AuthProvider
from core.auth.domain.auth_repo import AuthRepository, IdentityAlreadyExistsError
from core.user.domain.user import User


class ProvisionIdentity:
    def __init__(self, auth_repo: AuthRepository):
        self.auth_repo = auth_repo

    def execute(self, auth_id: str, email: str) -> Auth:
        if not email.strip():
            raise InvalidAuthCredentialsError("El email es requerido")

        existing = self.auth_repo.find_by_id(auth_id)
        if existing:
            return existing

        identity = self.auth_repo.get_identity(auth_id)
        if identity is None:
            raise InvalidAuthCredentialsError("El token de autenticación no es válido")

        if identity.provider.is_email():
            return self._provision_email(auth_id, email)

        if not identity.provider.is_oauth():
            raise UnsupportedAuthProviderError(
                "El proveedor debe ser un proveedor OAuth"
            )

        provider_id = identity.provider_id.value if identity.provider_id else None
        if not provider_id:
            raise InvalidAuthCredentialsError("El token de autenticación no es válido")

        existing_by_provider = self.auth_repo.find_by_provider_id(
            identity.provider,
            provider_id,
        )
        if existing_by_provider:
            return existing_by_provider

        return self._save(
            auth_id,
            email,
            provider=identity.provider,
            provider_id=provider_id,
        )

    def _provision_email(self, auth_id: str, email: str) -> Auth:
        return self._save(auth_id, email, provider=None, provider_id=None)

    def _save(
        self,
        auth_id: str,
        email: str,
        *,
        provider: AuthProvider | None,
        provider_id: str | None,
    ) -> Auth:
        email_vo = AuthEmail(email)
        if self.auth_repo.find_by_email(email_vo.value):
            raise EmailAlreadyExistsError("El email ya está registrado")

        user = User.create_empty()
        if provider is None:
            auth = Auth.create_with_email(
                id=auth_id,
                user_id=user.id.value,
                email=email_vo.value,
            )
        else:
            if not provider_id:
                raise InvalidAuthCredentialsError(
                    "El token de autenticación no es válido"
                )
            auth = Auth.create_with_oauth(
                id=auth_id,
                user_id=user.id.value,
                provider=provider,
                provider_id=provider_id,
                email=email_vo.value,
            )

        try:
            return self.auth_repo.save(user=user, auth=auth)
        except IdentityAlreadyExistsError as exc:
            raise EmailAlreadyExistsError("El email ya está registrado") from exc
