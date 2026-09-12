from core.auth.application.application_error import (
    EmailAlreadyExistsError,
    InvalidAuthCredentialsError,
    InvalidAuthProviderError,
    PasswordMismatchError,
)
from core.auth.domain.auth import Auth
from core.auth.domain.auth_email import AuthEmail
from core.auth.domain.auth_password import AuthPassword
from core.auth.domain.auth_provider import AuthProvider
from core.auth.domain.auth_repo import AuthRepository
from core.auth.infrastructure.error_infrastructure import IdentityAlreadyExistsError
from core.user.domain.user import User


class RegisterAuth:

    def __init__(
        self,
        auth_repo: AuthRepository,
    ):
        self.auth_repo = auth_repo

    def with_email(
        self,
        email: str,
        password: str,
        confirm_password: str,
    ) -> Auth:
        if password != confirm_password:
            raise PasswordMismatchError(
                "Las contraseñas no coinciden"
            )

        AuthPassword(password)
        email_vo = AuthEmail(email)

        if self.auth_repo.find_by_email(email_vo.value):
            raise EmailAlreadyExistsError(
                "El email ya está registrado"
            )

        user = User.create_empty()

        try:
            auth_id = self.auth_repo.create_identity(
                email_vo.value,
                password,
            )
        except IdentityAlreadyExistsError as exc:
            raise EmailAlreadyExistsError(
                "El email ya está registrado"
            ) from exc

        auth = Auth.create_with_email(
            id=auth_id,
            user_id=user.id.value,
            email=email_vo.value,
        )

        try:
            return self.auth_repo.save(
                user=user,
                auth=auth,
            )
        except Exception:
            try:
                self.auth_repo.delete_identity(auth_id)
            except Exception:
                pass
            raise

    def with_oauth(
        self,
        id: str,
        provider: AuthProvider,
        provider_id: str,
        email: str | None = None,
    ) -> Auth:
        if provider.is_email():
            raise InvalidAuthProviderError(
                "El proveedor de autenticación no es válido"
            )

        if not email:
            raise InvalidAuthCredentialsError(
                "El email es requerido"
            )

        existing = self.auth_repo.find_by_provider_id(
            provider,
            provider_id,
        )
        if existing:
            return existing

        email_vo = AuthEmail(email)

        if self.auth_repo.find_by_email(email_vo.value):
            raise EmailAlreadyExistsError(
                "El email ya está registrado"
            )

        user = User.create_empty()

        auth = Auth.create_with_oauth(
            id=id,
            user_id=user.id.value,
            provider=provider,
            provider_id=provider_id,
            email=email_vo.value,
        )

        return self.auth_repo.save(
            user=user,
            auth=auth,
        )

    def with_oauth_token(self, access_token: str) -> Auth:
        identity = self.auth_repo.get_oauth_identity(access_token)

        if not identity:
            raise InvalidAuthCredentialsError(
                "El token de autenticación no es válido"
            )

        return self.with_oauth(
            id=identity.id,
            provider=identity.provider,
            provider_id=identity.provider_id,
            email=identity.email,
        )
