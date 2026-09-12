from core.auth.domain.auth import Auth
from core.auth.domain.auth_email import AuthEmail
from core.auth.domain.auth_provider import AuthProvider
from core.auth.domain.auth_repo import AuthRepository, OAuthIdentity
from core.auth.infrastructure.email_crypto import EmailCrypto
from core.auth.infrastructure.error_infrastructure import (
    AuthCreationError,
    IdentityAlreadyExistsError,
)
from core.user.domain.user import User
from db.db_client import DBClient


class AuthSupabaseRepo(AuthRepository):

    def __init__(
        self,
        db_client: DBClient,
        email_crypto: EmailCrypto,
    ):
        self._db = db_client.get_db()
        self.email_crypto = email_crypto

    def create_identity(
        self,
        email: str,
        password: str,
    ) -> str:
        try:
            response = self._db.auth.admin.create_user({
                "email": email,
                "password": password,
                "email_confirm": True,
            })
        except Exception as exc:
            if self._is_duplicate_identity(exc):
                raise IdentityAlreadyExistsError(
                    "El email ya está registrado"
                ) from exc
            raise AuthCreationError(
                "Error al crear el usuario en Supabase"
            ) from exc

        if not response.user:
            raise AuthCreationError(
                "Error al crear el usuario en Supabase"
            )

        return response.user.id

    def delete_identity(
        self,
        auth_id: str,
    ) -> None:
        try:
            self._db.auth.admin.delete_user(auth_id)
        except Exception as exc:
            raise AuthCreationError(
                "Error al eliminar el usuario en Supabase"
            ) from exc

    def save(
        self,
        user: User,
        auth: Auth,
    ) -> Auth:
        if auth.email is None:
            raise AuthCreationError(
                "El email es requerido"
            )

        email_encrypted = self.email_crypto.encrypt(auth.email)
        email_hmac = self.email_crypto.hmac(auth.email)

        try:
            self._db.rpc(
                "create_user_and_auth",
                {
                    "p_user_id": user.id.value,
                    "p_auth_id": auth.id.value,
                    "p_email_encrypted": email_encrypted,
                    "p_email_hmac": email_hmac,
                    "p_provider": (
                        auth.provider_method.provider.value
                    ),
                    "p_provider_id": (
                        auth.provider_method.provider_id.value
                        if auth.provider_method.provider_id
                        else None
                    ),
                },
            ).execute()
        except Exception as exc:
            raise AuthCreationError(
                "Error al guardar el usuario"
            ) from exc

        return auth

    def find_by_email(self, email: str) -> Auth | None:
        email_hmac = self.email_crypto.hmac(AuthEmail(email))
        return self._find_auth({"email_hmac": email_hmac})

    def find_by_provider_id(
        self,
        provider: AuthProvider,
        provider_id: str,
    ) -> Auth | None:
        return self._find_auth({
            "provider": provider.value,
            "provider_id": provider_id,
        })

    def verify_password(self, email: str, password: str) -> bool:
        try:
            response = self._db.auth.sign_in_with_password({
                "email": email,
                "password": password,
            })
        except Exception:
            return False

        return response.user is not None

    def get_oauth_identity(
        self,
        access_token: str,
    ) -> OAuthIdentity | None:
        try:
            response = self._db.auth.get_user(access_token)
        except Exception:
            return None

        user = response.user
        if user is None:
            return None

        identities = user.identities or []
        google = next(
            (
                identity
                for identity in identities
                if identity.provider == "google"
            ),
            None,
        )
        if google is None:
            return None

        identity_data = google.identity_data or {}
        provider_id = (
            identity_data.get("sub")
            or getattr(google, "identity_id", None)
            or google.id
        )
        if not provider_id:
            return None

        return OAuthIdentity(
            id=user.id,
            provider=AuthProvider.GOOGLE,
            provider_id=str(provider_id),
            email=user.email,
        )

    def _find_auth(self, filters: dict) -> Auth | None:
        query = self._db.table("auth").select("*")
        for column, value in filters.items():
            query = query.eq(column, value)

        try:
            response = query.limit(1).execute()
        except Exception as exc:
            raise AuthCreationError(
                "Error al buscar el usuario"
            ) from exc

        rows = response.data or []
        if not rows:
            return None

        return self._row_to_auth(rows[0])

    def _row_to_auth(self, row: dict) -> Auth:
        email = self.email_crypto.decrypt(row["email_encrypted"])
        return Auth.from_primitive({
            "id": row["id"],
            "user_id": row["user_id"],
            "email": email.value,
            "created_at": row["created_at"],
            "provider_method": {
                "provider": row["provider"],
                "provider_id": row["provider_id"],
            },
        })

    @staticmethod
    def _is_duplicate_identity(exc: Exception) -> bool:
        message = str(exc).lower()
        return "already" in message or "registered" in message or "exists" in message
