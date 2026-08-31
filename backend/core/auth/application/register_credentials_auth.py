from backend.core.auth.application.error_application import PasswordNotMatchError
from backend.core.user.domain.user import User
from core.auth.domain.auth import Auth
from core.auth.domain.auth_repo import AuthRepo, RegisterAuthResult

class RegisterCredentialsAuth:
    def __init__(self, auth_repo: AuthRepo):
        self._auth_repo = auth_repo

    def register(self, email: str, password: str, confirm_password: str, name: str ) -> RegisterAuthResult:
        if password != confirm_password:
            raise PasswordNotMatchError( "Las contraseñas no coinciden" )
        
        user = User.create(name=name, avatar_url=None, description=None)
        auth = Auth.create(email=email, password=password, user=user.id)

        