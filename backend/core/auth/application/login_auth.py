from core.auth.application.application_error import (
    EmailNotFoundError,
    InvalidAuthProviderError,
    PasswordMismatchError,
)
from core.auth.domain.auth import Auth
from core.auth.domain.auth_email import AuthEmail
from core.auth.domain.auth_repo import AuthRepository


class LoginAuth:
    def __init__(self, auth_repo: AuthRepository):
        self.auth_repo = auth_repo

    def with_email(self, email: str, password: str) -> Auth:
        email_vo = AuthEmail(email)
        auth = self.auth_repo.find_by_email(email_vo.value)

        if not auth:
            raise EmailNotFoundError("El email no existe")

        if auth.provider_method.provider.is_oauth():
            raise InvalidAuthProviderError(
                "Esta cuenta se registra con Google"
            )

        if not self.auth_repo.verify_password(email_vo.value, password):
            raise PasswordMismatchError("La contraseña no es correcta")

        return auth
