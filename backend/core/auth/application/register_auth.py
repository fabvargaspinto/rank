from core.auth.domain.auth import Auth
from core.auth.domain.auth_repo import AuthRepo, RegisterAuthResult

class RegisterAuth:
    def __init__(self, auth_repo: AuthRepo):
        self._auth_repo = auth_repo

    def register(self, email: str, password: str, provider: str, name: str) -> RegisterAuthResult:
        print("register " ,  email, password, provider, name)
        self._auth_repo.register(email, password, provider, name)
        