from core.auth.domain.auth import Auth
from core.auth.domain.email_protector import EmailProtector
from core.auth.domain.auth_repo import AuthSession
from core.auth.infraestructure.error_infra import (
    AuthAlreadyExistsError,
    InvalidCredentialsError,
)
from core.share.infraestructure.database.supabase_client import SupabaseClient
from core.share.infraestructure.infra_error import DatabaseError
from core.user.domain.user import User
from core.user.infraestructure.error_infra import UserNameAlreadyExistsError


class AuthSupabaseRepo:
    def __init__(
        self,
        supabase_client: SupabaseClient,
        email_protector: EmailProtector,
    ):
        self._supabase_client = supabase_client
        self._client = supabase_client.get_client()
        self._email_protector = email_protector
        self.table = "auths"

    def login(self, email: str, password: str) -> AuthSession:
        auth_client = self._supabase_client.create_auth_client()
        try:
            response = auth_client.auth.sign_in_with_password(
                {
                    "email": email,
                    "password": password,
                }
            )
        except Exception as error:
            raise InvalidCredentialsError("Invalid email or password") from error

        session = getattr(response, "session", None)
        access_token = getattr(session, "access_token", None) if session else None
        refresh_token = getattr(session, "refresh_token", None) if session else None
        expires_in = getattr(session, "expires_in", None) if session else None
        if not access_token or not refresh_token or expires_in is None:
            raise InvalidCredentialsError("Invalid email or password")

        return AuthSession(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=int(expires_in),
        )

    def register(
        self,
        auth: Auth,
        user: User,
        password: str | None = None,
    ) -> None:
        identity_id: str | None = None
        try:
            if auth.provider.is_credentials():
                if not password:
                    raise DatabaseError("Password is required to register credentials")
                identity_id = self._create_identity(
                    email=auth.email.value,
                    password=password,
                    name=user.name.value,
                    user_id=user.id.value,
                )
            self._persist_user_and_auth(auth, user)
        except Exception:
            if identity_id is not None:
                try:
                    self._delete_identity(identity_id)
                except Exception as rollback_error:
                    raise DatabaseError(
                        "Error registering user and auth: identity rollback failed"
                    ) from rollback_error
            raise

    def _create_identity(
        self,
        email: str,
        password: str,
        name: str,
        user_id: str,
    ) -> str:
        try:
            response = self._client.auth.admin.create_user(
                {
                    "id": user_id,
                    "email": email,
                    "password": password,
                    "email_confirm": True,
                    "user_metadata": {"name": name},
                }
            )
        except Exception as error:
            raise self._to_identity_error(error) from error

        identity = getattr(response, "user", None)
        identity_id = getattr(identity, "id", None) if identity else None
        return str(identity_id or user_id)

    def _delete_identity(self, identity_id: str) -> None:
        try:
            self._client.auth.admin.delete_user(identity_id)
        except Exception as error:
            message = getattr(error, "message", None) or str(error)
            lowered = message.lower()
            if "not found" in lowered or "404" in lowered:
                return
            raise DatabaseError(f"Error deleting auth identity: {message}") from error

    def _persist_user_and_auth(self, auth: Auth, user: User) -> None:
        email_encrypted = self._email_protector.encrypt(auth.email)
        email_hmac = self._email_protector.generate_email_hmac_identifier(auth.email)

        try:
            self._client.rpc(
                "register_user_with_auth",
                {
                    "p_user_id": user.id.value,
                    "p_name": user.name.value,
                    "p_avatar_url": user.avatar_url.value if user.avatar_url else None,
                    "p_description": (
                        user.description.value if user.description else ""
                    ),
                    "p_user_created_at": user.created_at.value.isoformat(),
                    "p_user_updated_at": user.updated_at.value.isoformat(),
                    "p_auth_id": auth.id.value,
                    "p_provider": str(auth.provider),
                    "p_email_encrypted": email_encrypted,
                    "p_email_hmac": email_hmac,
                    "p_provider_id": auth.provider_id,
                    "p_auth_created_at": auth.created_at.value.isoformat(),
                },
            ).execute()
        except Exception as error:
            raise self._to_register_error(error) from error

    @staticmethod
    def _to_identity_error(error: Exception) -> Exception:
        message = getattr(error, "message", None) or str(error)
        lowered = message.lower()

        if "already" in lowered or "registered" in lowered or "exists" in lowered:
            return AuthAlreadyExistsError("Auth email already exists")

        return DatabaseError(f"Error creating auth identity: {message}")

    @staticmethod
    def _to_register_error(error: Exception) -> Exception:
        message = getattr(error, "message", None) or str(error)

        if "USER_NAME_ALREADY_EXISTS" in message:
            return UserNameAlreadyExistsError("User name already exists")
        if "AUTH_EMAIL_ALREADY_EXISTS" in message:
            return AuthAlreadyExistsError("Auth email already exists")
        if "AUTH_OAUTH_ALREADY_EXISTS" in message:
            return AuthAlreadyExistsError("OAuth identity already exists")
        if "AUTH_PROVIDER_ALREADY_EXISTS" in message:
            return AuthAlreadyExistsError("Auth provider already exists")

        return DatabaseError(f"Error registering user and auth: {message}")
