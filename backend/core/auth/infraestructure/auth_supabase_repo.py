from supabase import Client


from core.auth.domain.auth_repo import RegisterAuthResult
from core.auth.domain.auth import Auth
from core.auth.domain.auth_email import Email
from core.auth.domain.auth_password import Password
from core.user.user_id import UserId
from core.share.infraestructure.infra_error import AuthAlreadyExistsError, DatabaseError


class AuthSupabaseRepo:
    def __init__(self, client: Client) -> None:
        self._client = client

    def register(self, email: Email, password: Password) -> RegisterAuthResult:
        try:
            response = self._client.auth.sign_up(
                {
                    "email": email.value,
                    "password": password.value,
                }
            )
        except Exception as error:
            raise AuthAlreadyExistsError("Email is already registered") from error

        user = response.user
        if user is None or not user.id:
            raise AuthAlreadyExistsError("Email is already registered")

        identities = getattr(user, "identities", None)
        if identities is not None and len(identities) == 0:
            raise AuthAlreadyExistsError("Email is already registered")

        user_id = UserId(user.id)
        session = response.session
        return RegisterAuthResult(
            auth=Auth.create_with_credentials(user_id, email.value),
            access_token=session.access_token if session else None,
            refresh_token=session.refresh_token if session else None,
            expires_in=session.expires_in if session else None,
        )
