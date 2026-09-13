from core.auth.application.application_error import (
    EmailAlreadyExistsError,
    InvalidAuthCredentialsError,
)
from core.auth.domain.auth import Auth
from core.auth.domain.auth_email import AuthEmail
from core.auth.domain.auth_repo import AuthIdentity, AuthRepository
from core.user.domain.user import User


class EnsureUserProvisioned:
    def __init__(self, auth_repo: AuthRepository):
        self.auth_repo = auth_repo

    def execute(self, access_token: str) -> Auth:
        identity = self.auth_repo.get_identity(access_token)

        if not identity:
            raise InvalidAuthCredentialsError(
                "El token de autenticación no es válido"
            )

        if not identity.email:
            raise InvalidAuthCredentialsError(
                "El email es requerido"
            )

        existing_by_id = self.auth_repo.find_by_id(identity.id)
        if existing_by_id:
            return existing_by_id

        if identity.provider.is_oauth():
            if not identity.provider_id:
                raise InvalidAuthCredentialsError(
                    "El token de autenticación no es válido"
                )

            existing_by_provider = self.auth_repo.find_by_provider_id(
                identity.provider,
                identity.provider_id,
            )
            if existing_by_provider:
                return existing_by_provider

        email_vo = AuthEmail(identity.email)

        if self.auth_repo.find_by_email(email_vo.value):
            raise EmailAlreadyExistsError(
                "El email ya está registrado"
            )

        user = User.create_empty()
        auth = self._auth_from_identity(identity, user.id.value, email_vo.value)

        return self.auth_repo.save(
            user=user,
            auth=auth,
        )

    @staticmethod
    def _auth_from_identity(
        identity: AuthIdentity,
        user_id: str,
        email: str,
    ) -> Auth:
        if identity.provider.is_email():
            return Auth.create_with_email(
                id=identity.id,
                user_id=user_id,
                email=email,
            )

        if not identity.provider_id:
            raise InvalidAuthCredentialsError(
                "El token de autenticación no es válido"
            )

        return Auth.create_with_oauth(
            id=identity.id,
            user_id=user_id,
            provider=identity.provider,
            provider_id=identity.provider_id,
            email=email,
        )
