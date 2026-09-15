from config.crypto_setings import CryptoSettings
from core.auth.domain.auth import Auth
from core.auth.domain.auth_provider import AuthProvider
from core.auth.infrastructure.auth_mapper import AuthMapper
from core.auth.infrastructure.email_crypto import EmailCrypto

AUTH_ID = "660e8400-e29b-41d4-a716-446655440000"
USER_ID = "550e8400-e29b-41d4-a716-446655440000"
EMAIL = "test@example.com"
GOOGLE_PROVIDER_ID = "google-user-123"


def _mapper() -> AuthMapper:
    return AuthMapper(
        EmailCrypto(
            CryptoSettings(
                email_encryption_key="00" * 32,
                email_hmac_key="11" * 32,
            )
        )
    )


def _email_auth() -> Auth:
    return Auth.create_with_email(
        id=AUTH_ID,
        user_id=USER_ID,
        email=EMAIL,
    )


def _oauth_auth() -> Auth:
    return Auth.create_with_oauth(
        id=AUTH_ID,
        user_id=USER_ID,
        provider=AuthProvider.GOOGLE,
        provider_id=GOOGLE_PROVIDER_ID,
        email=EMAIL,
    )


class TestAuthMapper:
    def test_to_row_uses_public_auth_columns(self):
        mapper = _mapper()
        auth = _email_auth()

        row = mapper.to_row(auth)

        assert set(row) == {
            "id",
            "user_id",
            "email_encrypted",
            "email_hmac",
            "provider",
            "provider_id",
            "created_at",
        }
        assert row["id"] == AUTH_ID
        assert row["user_id"] == USER_ID
        assert row["provider"] == "EMAIL"
        assert row["provider_id"] is None
        assert row["created_at"] == auth.created_at.to_isoformat()
        assert EMAIL not in row["email_encrypted"]
        assert row["email_hmac"] == mapper.email_crypto.hmac(auth.email)

    def test_to_domain_rebuilds_email_auth_from_row(self):
        mapper = _mapper()
        auth = _email_auth()

        restored = mapper.to_domain(mapper.to_row(auth))

        assert restored == auth

    def test_to_domain_rebuilds_oauth_auth_from_row(self):
        mapper = _mapper()
        auth = _oauth_auth()

        restored = mapper.to_domain(mapper.to_row(auth))

        assert restored == auth
        assert restored.provider_method.provider is AuthProvider.GOOGLE
        assert restored.provider_method.provider_id.value == GOOGLE_PROVIDER_ID
        assert restored.email.value == EMAIL

    def test_to_row_does_not_embed_nested_provider_method(self):
        row = _mapper().to_row(_oauth_auth())

        assert "provider_method" not in row
        assert row["provider"] == "GOOGLE"
        assert row["provider_id"] == GOOGLE_PROVIDER_ID
