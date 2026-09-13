from core.auth.domain.auth import Auth
from core.auth.domain.auth_email import AuthEmail
from core.auth.domain.auth_provider import AuthProvider
from core.auth.domain.auth_repo import AuthIdentity, AuthRepository
from core.auth.infrastructure.email_crypto import EmailCrypto
from core.auth.infrastructure.error_infrastructure import AuthCreationError
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

    def find_by_id(self, auth_id: str) -> Auth | None:
        return self._find_auth({"id": auth_id})

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

    def get_identity(self, access_token: str) -> AuthIdentity | None:
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
        if google is not None:
            identity_data = google.identity_data or {}
            provider_id = (
                identity_data.get("sub")
                or getattr(google, "identity_id", None)
                or google.id
            )
            if not provider_id:
                return None

            return AuthIdentity(
                id=user.id,
                provider=AuthProvider.GOOGLE,
                provider_id=str(provider_id),
                email=user.email,
            )

        if user.email:
            return AuthIdentity(
                id=user.id,
                provider=AuthProvider.EMAIL,
                provider_id=None,
                email=user.email,
            )

        return None

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
