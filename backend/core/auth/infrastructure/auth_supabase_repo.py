from postgrest.exceptions import APIError

from core.auth.domain.auth import Auth
from db.db_error import DBPersistenceError
from core.auth.domain.auth_repo import AuthRepository
from core.auth.domain.email_crypto import EmailCrypto
from core.user.domain.user import User
from db.db_client import DBClient


class AuthSupabaseRepo(AuthRepository):
    def __init__(self, db_client: DBClient, email_crypto: EmailCrypto):
        self.db_client = db_client
        self.email_crypto = email_crypto

    def create_user(self, user: User, auth: Auth) -> None:
        try:
            self.db_client.get_db().rpc(
                "register_auth",
                {
                    "p_user_id": user.id.value,
                    "p_auth_id": auth.id.value,
                    "p_name": user.name.value if user.name else None,
                    "p_avatar_url": user.avatar.value if user.avatar else None,
                    "p_description": user.description.value if user.description else None,
                    "p_email": auth.email.value,
                    "p_email_encrypted": self.email_crypto.encrypt(auth.email),
                    "p_email_hmac": self.email_crypto.hmac(auth.email),
                    "p_provider": auth.provider.value,
                    "p_password": auth.password.value if auth.password else None,
                    "p_oauth_provider": auth.oauth_provider.value if auth.oauth_provider else None,
                    "p_provider_id": auth.provider_id.value if auth.provider_id else None,
                },
            ).execute()
        except APIError as error:
            raise DBPersistenceError(error.message) from error
