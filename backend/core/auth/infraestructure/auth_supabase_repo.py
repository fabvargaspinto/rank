from datetime import datetime

from postgrest.exceptions import APIError

from core.auth.infraestructure.error_infra import AuthAlreadyExistsError
from core.share.infraestructure.database.supabase_client import SupabaseClient
from core.share.infraestructure.infra_error import DatabaseError
from core.user.infraestructure.error_infra import UserNameAlreadyExistsError


class AuthSupabaseRepo:
    def __init__(self, supabase_client: SupabaseClient):
        self._client = supabase_client.get_client()
        self.table = "auths"

    def register_credentials(
        self,
        user_id: str,
        name: str,
        avatar_url: str | None,
        description: str,
        user_created_at: datetime,
        user_updated_at: datetime,
        auth_id: str,
        email_encrypted: str,
        email_hmac: str,
        provider: str,
        auth_created_at: datetime,
    ) -> None:
        self._register_user_with_auth(
            user_id=user_id,
            name=name,
            avatar_url=avatar_url,
            description=description,
            user_created_at=user_created_at,
            user_updated_at=user_updated_at,
            auth_id=auth_id,
            provider=provider,
            email_encrypted=email_encrypted,
            email_hmac=email_hmac,
            provider_id=None,
            auth_created_at=auth_created_at,
        )

    def register_oauth(
        self,
        user_id: str,
        name: str,
        avatar_url: str | None,
        description: str,
        user_created_at: datetime,
        user_updated_at: datetime,
        auth_id: str,
        provider: str,
        email_encrypted: str,
        email_hmac: str,
        provider_id: str,
        auth_created_at: datetime,
    ) -> None:
        self._register_user_with_auth(
            user_id=user_id,
            name=name,
            avatar_url=avatar_url,
            description=description,
            user_created_at=user_created_at,
            user_updated_at=user_updated_at,
            auth_id=auth_id,
            provider=provider,
            email_encrypted=email_encrypted,
            email_hmac=email_hmac,
            provider_id=provider_id,
            auth_created_at=auth_created_at,
        )

    def _register_user_with_auth(
        self,
        user_id: str,
        name: str,
        avatar_url: str | None,
        description: str,
        user_created_at: datetime,
        user_updated_at: datetime,
        auth_id: str,
        provider: str,
        email_encrypted: str,
        email_hmac: str,
        provider_id: str | None,
        auth_created_at: datetime,
    ) -> None:
        try:
            self._client.rpc(
                "register_user_with_auth",
                {
                    "p_user_id": user_id,
                    "p_name": name,
                    "p_avatar_url": avatar_url,
                    "p_description": description,
                    "p_user_created_at": user_created_at.isoformat(),
                    "p_user_updated_at": user_updated_at.isoformat(),
                    "p_auth_id": auth_id,
                    "p_provider": provider,
                    "p_email_encrypted": email_encrypted,
                    "p_email_hmac": email_hmac,
                    "p_provider_id": provider_id,
                    "p_auth_created_at": auth_created_at.isoformat(),
                },
            ).execute()
        except APIError as error:
            raise self._to_register_error(error) from error
        except Exception as error:
            raise DatabaseError("Error registering user and auth") from error

    @staticmethod
    def _to_register_error(error: APIError) -> Exception:
        message = error.message or str(error)

        if "USER_NAME_ALREADY_EXISTS" in message:
            return UserNameAlreadyExistsError("User name already exists")
        if "AUTH_EMAIL_ALREADY_EXISTS" in message:
            return AuthAlreadyExistsError("Auth email already exists")
        if "AUTH_OAUTH_ALREADY_EXISTS" in message:
            return AuthAlreadyExistsError("OAuth identity already exists")
        if "AUTH_PROVIDER_ALREADY_EXISTS" in message:
            return AuthAlreadyExistsError("Auth provider already exists")

        return DatabaseError(f"Error registering user and auth: {message}")
