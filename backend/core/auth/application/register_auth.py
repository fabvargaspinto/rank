from core.auth.domain.auth_email import Email
from core.auth.domain.auth_password import Password
from core.auth.domain.auth_error import DuplicateAuthError
from core.auth.domain.auth_repo import AuthRepo, RegisterAuthResult
from core.share.infraestructure.infra_error import AuthAlreadyExistsError, DatabaseError


class RegisterAuth:
    def __init__(self, auth_repo: AuthRepo) -> None:
        self._auth_repo = auth_repo

    def execute(self, email: str, password: str) -> RegisterAuthResult:
        try:
            return self._auth_repo.register(Email(email), Password(password))
        except AuthAlreadyExistsError as error:
            raise DuplicateAuthError("Email is already registered") from error
        except DatabaseError:
            raise
