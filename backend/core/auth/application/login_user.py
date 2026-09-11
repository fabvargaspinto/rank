from dataclasses import dataclass

from core.auth.application.application_error import InvalidAuthCredentialsError
from core.auth.application.application_error import InvalidAuthProviderError
from core.auth.domain.auth_provider import AuthProvider
from core.auth.domain.auth_repo import AuthRepository
from core.shared.infrastructure.infrastructure_error import DBError


@dataclass(frozen=True)
class AuthSession:
    access_token: str
    refresh_token: str
    user_id: str
    auth_id: str

    def to_primitive(self) -> dict:
        return {
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "user_id": self.user_id,
            "auth_id": self.auth_id,
        }


class LoginUserUseCase:
    def __init__(self, auth_repository: AuthRepository):
        self.auth_repository = auth_repository

    def with_email(self, email: str, password: str) -> AuthSession:
        auth = self.auth_repository.find_auth_by_email(email)
        if not auth or not self.auth_repository.auth_has_provider(
            auth.id, AuthProvider.EMAIL
        ):
            raise InvalidAuthCredentialsError("Credenciales inválidas")

        try:
            access_token, refresh_token = self.auth_repository.login_with_email(
                auth.email.value, password
            )
        except DBError as error:
            raise InvalidAuthCredentialsError("Credenciales inválidas") from error

        return AuthSession(
            access_token=access_token,
            refresh_token=refresh_token,
            user_id=auth.user_id.value,
            auth_id=auth.id.value,
        )

    def with_oauth(
        self,
        email: str,
        provider: AuthProvider,
        provider_id: str,
    ) -> AuthSession:
        if not provider.is_oauth():
            raise InvalidAuthProviderError("El proveedor debe ser un proveedor OAuth")

        auth = self.auth_repository.find_auth_by_email(email)
        method = (
            self.auth_repository.find_auth_method(auth.id, provider) if auth else None
        )
        if (
            not auth
            or method is None
            or method.provider_id is None
            or method.provider_id.value != provider_id
        ):
            raise InvalidAuthCredentialsError("Credenciales inválidas")

        try:
            access_token, refresh_token = self.auth_repository.login_with_oauth(
                auth.email.value
            )
        except DBError as error:
            raise InvalidAuthCredentialsError("Credenciales inválidas") from error

        return AuthSession(
            access_token=access_token,
            refresh_token=refresh_token,
            user_id=auth.user_id.value,
            auth_id=auth.id.value,
        )
