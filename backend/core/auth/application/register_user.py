from core.auth.domain.auth import Auth
from core.auth.domain.auth_email import AuthEmail
from core.auth.domain.auth_error import InvalidAuthPasswordError
from core.auth.domain.auth_oauth_provider import AuthOauthProvider
from core.auth.domain.auth_password import AuthPassword
from core.auth.domain.auth_provider_id import AuthProviderId
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

        user = User.create_empty()
        auth = Auth.create_email_auth(
            user.id,
            AuthEmail(email),
            AuthPassword(password),
        )
        self.auth_repository.create_user(user, auth)

    def with_oauth_provider(
        self,
        email: str,
        oauth_provider: AuthOauthProvider,
        oauth_provider_id: str,
    ) -> None:
        user = User.create_empty()
        auth = Auth.create_oauth_auth(
            user.id,
            AuthEmail(email),
            oauth_provider,
            AuthProviderId(oauth_provider_id),
        )
        self.auth_repository.create_user(user, auth)

  
