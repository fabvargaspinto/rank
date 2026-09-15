from core.auth.domain.auth import Auth
from core.auth.domain.auth_created_at import AuthCreatedAt
from core.auth.domain.auth_id import AuthId
from core.auth.domain.auth_method import AuthMethod
from core.auth.domain.auth_provider import AuthProvider
from core.auth.infrastructure.email_crypto import EmailCrypto
from core.user.domain.user_id import UserId


class AuthMapper:
    def __init__(self, email_crypto: EmailCrypto):
        self.email_crypto = email_crypto

    def to_domain(self, row: dict) -> Auth:
        provider = AuthProvider.from_string(row["provider"])
        if provider.is_email():
            method = AuthMethod.email()
        else:
            method = AuthMethod.oauth(provider, row["provider_id"])

        return Auth(
            id=AuthId(row["id"]),
            user_id=UserId(row["user_id"]),
            email=self.email_crypto.decrypt(row["email_encrypted"]),
            created_at=AuthCreatedAt.from_isoformat(row["created_at"]),
            provider_method=method,
        )

    def to_row(self, auth: Auth) -> dict:
        email = auth.email
        return {
            "id": auth.id.value,
            "user_id": auth.user_id.value,
            "email_encrypted": self.email_crypto.encrypt(email),
            "email_hmac": self.email_crypto.hmac(email),
            "provider": auth.provider_method.provider.value,
            "provider_id": (
                auth.provider_method.provider_id.value
                if auth.provider_method.provider_id
                else None
            ),
            "created_at": auth.created_at.to_isoformat(),
        }
