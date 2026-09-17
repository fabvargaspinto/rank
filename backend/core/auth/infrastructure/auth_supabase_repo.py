from postgrest.exceptions import APIError

from core.auth.domain.auth import Auth
from core.auth.domain.auth_email import AuthEmail
from core.auth.domain.auth_provider import AuthProvider
from core.auth.domain.auth_repo import (
    AuthIdentity,
    AuthRepository,
    IdentityAlreadyExistsError,
)
from core.auth.infrastructure.auth_mapper import AuthMapper
from core.auth.infrastructure.email_crypto import EmailCrypto
from core.auth.infrastructure.error_infrastructure import AuthCreationError
from core.auth.infrastructure.postgres_error import is_unique_violation
from core.user.domain.user import User
from db.db_client import DBClient
from core.user.infrastructure.user_mapper import UserMapper


class AuthSupabaseRepo(AuthRepository):

    def __init__(
        self,
        db_client: DBClient,
        email_crypto: EmailCrypto,
    ):
        self._db = db_client.get_db()
        self.email_crypto = email_crypto
        self._mapper = AuthMapper(email_crypto)
        self._user_mapper = UserMapper()

    def save(
        self,
        user: User,
        auth: Auth,
    ) -> Auth:
        row = self._mapper.to_row(auth)
        user_row = self._user_mapper.to_row(user)


        try:
            self._db.rpc(
                "create_user_and_auth",
                {
                    "p_user_id": user_row["id"],
                    "p_auth_id": row["id"],
                    "p_email_encrypted": row["email_encrypted"],
                    "p_email_hmac": row["email_hmac"],
                    "p_provider": row["provider"],
                    "p_provider_id": row["provider_id"],
                },
            ).execute()
        except APIError as exc:
            if is_unique_violation(exc):
                raise IdentityAlreadyExistsError(
                    "La identidad ya existe"
                ) from exc
            raise AuthCreationError(
                "Error al guardar el usuario"
            ) from exc
        except Exception as exc:
            raise AuthCreationError(
                "Error al guardar el usuario"
            ) from exc

        persisted = self.find_by_id(auth.id.value)
        if persisted is None:
            raise AuthCreationError(
                "Error al guardar el usuario"
            )

        return persisted

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

    def get_identity(self, auth_id: str) -> AuthIdentity | None:
        try:
            response = self._db.auth.admin.get_user_by_id(auth_id)
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

        row = rows[0]
        if not isinstance(row, dict):
            raise AuthCreationError("Error al buscar el usuario")
        return self._mapper.to_domain(row)
