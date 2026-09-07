from core.auth.domain.auth_email import Email
from core.auth.domain.auth_repo import AuthRepo, AuthSession
from core.auth.infraestructure.error_infra import InvalidCredentialsError


class LoginAuth:
    def __init__(self, auth_repo: AuthRepo):
        self._auth_repo = auth_repo

    def login(self, email: str, password: str) -> AuthSession:
        Email(email)
        if not password:
            raise InvalidCredentialsError("Invalid email or password")
        return self._auth_repo.login(email, password)
