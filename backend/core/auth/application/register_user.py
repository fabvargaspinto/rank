from core.auth.application.application_error import AuthAlreadyExistsError
from core.auth.application.application_error import InvalidAuthProviderError
from core.auth.domain.auth import Auth
from core.auth.domain.auth_error import InvalidAuthPasswordError
from core.auth.domain.auth_method import AuthMethod
from core.auth.domain.auth_password import AuthPassword
from core.auth.domain.auth_provider import AuthProvider
from core.auth.domain.auth_repo import AuthRepository
from core.user.domain.user import User


class RegisterUserUseCase:
    def __init__(self, auth_repository: AuthRepository):
        self.auth_repository = auth_repository

    def with_email(
        self,
        email: str,
        password: str,
        confirm_password: str,
    ) -> None:
        if password != confirm_password:
            raise InvalidAuthPasswordError("Las contraseñas no coinciden")

        validated_password = AuthPassword(password)
        method = AuthMethod.email()
        existing = self.auth_repository.find_auth_by_email(email)

        if existing:
            if self.auth_repository.auth_has_provider(existing.id, AuthProvider.EMAIL):
                raise AuthAlreadyExistsError("El email ya está registrado")
            self.auth_repository.link_auth_provider(
                existing, method, validated_password.value
            )
            return

        user = User.create_empty()
        auth = Auth.create(user.id.value, email)
        self.auth_repository.create_user(
            user, auth, method, validated_password.value
        )

    def with_oauth(
        self,
        email: str,
        provider: AuthProvider,
        provider_id: str,
    ) -> None:
        if not provider.is_oauth():
            raise InvalidAuthProviderError("El proveedor debe ser un proveedor OAuth")

        method = AuthMethod.oauth(provider, provider_id)
        existing = self.auth_repository.find_auth_by_email(email)

        if existing:
            if self.auth_repository.auth_has_provider(existing.id, provider):
                raise AuthAlreadyExistsError("El email ya está registrado")
            self.auth_repository.link_auth_provider(existing, method)
            return

        user = User.create_empty()
        auth = Auth.create(user.id.value, email)
        self.auth_repository.create_user(user, auth, method)
