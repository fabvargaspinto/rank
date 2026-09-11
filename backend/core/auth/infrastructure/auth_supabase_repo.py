from postgrest.exceptions import APIError

from core.auth.domain.auth import Auth
from core.auth.domain.auth_email import AuthEmail
from core.auth.domain.auth_id import AuthId
from core.auth.domain.auth_method import AuthMethod
from core.auth.domain.auth_provider import AuthProvider
from core.auth.domain.auth_repo import AuthRepository
from core.auth.domain.email_crypto import EmailCrypto
from core.shared.infrastructure.infrastructure_error import DBError
from core.user.domain.user import User
from db.db_client import DBClient


class AuthSupabaseRepo(AuthRepository):
    def __init__(self, db_client: DBClient, email_crypto: EmailCrypto):
        self.db_client = db_client
        self.email_crypto = email_crypto
        self.table = "auth"
        self.providers_table = "auth_providers"

    def create_user(
        self,
        user: User,
        auth: Auth,
        method: AuthMethod,
        password: str | None = None,
    ) -> None:
        try:
            self.db_client.get_db().rpc(
                "register_auth",
                {
                    "p_user_id": user.id.value,
                    "p_auth_id": auth.id.value,
                    "p_name": user.name.value if user.name else None,
                    "p_avatar_url": user.avatar.value if user.avatar else None,
                    "p_description": (
                        user.description.value if user.description else None
                    ),
                    "p_email": auth.email.value,
                    "p_email_encrypted": self.email_crypto.encrypt(auth.email),
                    "p_email_hmac": self.email_crypto.hmac(auth.email),
                    "p_provider": method.provider.value,
                    "p_password": password,
                    "p_provider_id": (
                        method.provider_id.value if method.provider_id else None
                    ),
                },
            ).execute()
        except APIError as error:
            raise DBError(error.message) from error

    def link_auth_provider(
        self,
        auth: Auth,
        method: AuthMethod,
        password: str | None = None,
    ) -> None:
        try:
            self.db_client.get_db().rpc(
                "link_auth_provider",
                {
                    "p_auth_id": auth.id.value,
                    "p_email": auth.email.value,
                    "p_provider": method.provider.value,
                    "p_password": password,
                    "p_provider_id": (
                        method.provider_id.value if method.provider_id else None
                    ),
                },
            ).execute()
        except APIError as error:
            raise DBError(error.message) from error

    def find_auth_by_email(self, email: str) -> Auth | None:
        email_hmac = self.email_crypto.hmac(AuthEmail(email))
        try:
            response = (
                self.db_client.get_db()
                .table(self.table)
                .select("*")
                .eq("email_hmac", email_hmac)
                .limit(1)
                .execute()
            )
        except APIError as error:
            raise DBError(error.message) from error

        if not response.data:
            return None

        row = response.data[0]
        decrypted_email = self.email_crypto.decrypt(row["email_encrypted"])
        return Auth.from_primitive(row, decrypted_email)

    def auth_has_provider(self, auth_id: AuthId, provider: AuthProvider) -> bool:
        try:
            response = (
                self.db_client.get_db()
                .table(self.providers_table)
                .select("id")
                .eq("auth_id", auth_id.value)
                .eq("provider", provider.value)
                .limit(1)
                .execute()
            )
        except APIError as error:
            raise DBError(error.message) from error

        return bool(response.data)
