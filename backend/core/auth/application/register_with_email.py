from core.auth.application.application_error import (
    EmailAlreadyExistsError,
    InvalidAuthCredentialsError,
)
from core.auth.domain.auth import Auth
from core.auth.domain.auth_email import AuthEmail
from core.auth.domain.auth_repo import AuthRepository, IdentityAlreadyExistsError
from core.user.domain.user import User


class RegisterWithEmail:
    def __init__(self, auth_repo: AuthRepository):
        self.auth_repo = auth_repo

    def execute(self, auth_id: str, email: str) -> Auth:
        if not email.strip():
            raise InvalidAuthCredentialsError(
                "El email es requerido"
            )

        existing = self.auth_repo.find_by_id(auth_id)
        if existing:
            return existing

        email_vo = AuthEmail(email)
        if self.auth_repo.find_by_email(email_vo.value):
            raise EmailAlreadyExistsError(
                "El email ya está registrado"
            )

        user = User.create_empty()
        auth = Auth.create_with_email(
            id=auth_id,
            user_id=user.id.value,
            email=email_vo.value,
        )

        try:
            return self.auth_repo.save(user=user, auth=auth)
        except IdentityAlreadyExistsError as exc:
            raise EmailAlreadyExistsError(
                "El email ya está registrado"
            ) from exc
