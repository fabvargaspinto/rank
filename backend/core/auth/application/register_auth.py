from core.auth.application.error_application import (
    InvalidProviderError,
    PasswordNotMatchError,
)
from core.auth.domain.auth import Auth
from core.auth.domain.auth_email import Email
from core.auth.domain.auth_provider import Provider
from core.auth.domain.auth_repo import AuthRepo, AuthSession, RegisterAuthResult
from core.user.application.register_user import RegisterUser


class RegisterAuth:
    def __init__(self, auth_repo: AuthRepo, register_user: RegisterUser):
        self._auth_repo = auth_repo
        self._register_user = register_user

    def register_with_credentials(
        self,
        email: str,
        name: str,
        password: str,
        confirm_password: str,
    ) -> RegisterAuthResult:
        if not password or not confirm_password:
            raise PasswordNotMatchError(
                "ingrese una contraseña y confirme la contraseña"
            )
        if password != confirm_password:
            raise PasswordNotMatchError("las contraseñas no coinciden")

        Auth.validate_password(password)
        

        user = self._register_user.register(name)
        auth = Auth.create_with_credentials(
            id=user.id.value,
            user_id=user.id,
            email=email,
        )
        self._auth_repo.register(auth, user, password=password)

        session = self._sign_in(email, password)
        return RegisterAuthResult(auth=auth, session=session)

    def register_with_google(
        self,
        email: str,
        name: str,
        provider_id: str,
    ) -> RegisterAuthResult:
        if not provider_id:
            raise InvalidProviderError("OAuth provider id is required")

        user = self._register_user.register(name)
        auth = Auth.create_from_oauth(
            user_id=user.id,
            email=email,
            provider=Provider.from_google(),
            provider_id=provider_id,
        )
        self._auth_repo.register(auth, user)
        return RegisterAuthResult(auth=auth)

    def _sign_in(self, email: str, password: str) -> AuthSession | None:
        try:
            return self._auth_repo.login(email, password)
        except Exception:
            return None
