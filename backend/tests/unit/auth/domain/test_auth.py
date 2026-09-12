from dataclasses import FrozenInstanceError

import pytest

from core.auth.domain.auth import Auth
from core.auth.domain.auth_method import AuthMethod
from core.auth.domain.auth_provider import AuthProvider


AUTH_ID = "660e8400-e29b-41d4-a716-446655440000"
USER_ID = "550e8400-e29b-41d4-a716-446655440000"
EMAIL = "test@example.com"
GOOGLE_PROVIDER_ID = "google-user-123"


def create_email_auth(email: str = EMAIL) -> Auth:
    return Auth.create_with_email(
        id=AUTH_ID,
        user_id=USER_ID,
        email=email,
    )


def create_oauth_auth() -> Auth:
    return Auth.create_with_oauth(
        id=AUTH_ID,
        user_id=USER_ID,
        provider=AuthProvider.GOOGLE,
        provider_id=GOOGLE_PROVIDER_ID,
    )


class TestAuth:

    def test_should_create_auth_with_email(self):
        auth = create_email_auth()

        assert auth.id.value == AUTH_ID
        assert auth.user_id.value == USER_ID
        assert auth.email.value == EMAIL
        assert auth.created_at is not None

        assert auth.provider_method.provider == AuthProvider.EMAIL
        assert auth.provider_method.provider_id is None

    def test_should_normalize_email_when_creating_auth(self):
        auth = create_email_auth(email="TEST@EXAMPLE.COM")

        assert auth.email.value == "test@example.com"

    def test_should_create_auth_with_google(self):
        auth = create_oauth_auth()

        assert auth.id.value == AUTH_ID
        assert auth.user_id.value == USER_ID
        assert auth.email is None
        assert auth.created_at is not None

        assert auth.provider_method.provider == AuthProvider.GOOGLE
        assert auth.provider_method.provider_id.value == GOOGLE_PROVIDER_ID

    def test_should_create_auth_with_oauth_provider(self):
        auth = create_oauth_auth()

        assert auth.provider_method == AuthMethod.oauth(
            provider=AuthProvider.GOOGLE,
            provider_id=GOOGLE_PROVIDER_ID,
        )

    def test_should_convert_email_auth_to_primitive(self):
        auth = create_email_auth()

        primitive = auth.to_primitive()

        assert primitive["id"] == AUTH_ID
        assert primitive["user_id"] == USER_ID
        assert primitive["email"] == EMAIL
        assert primitive["created_at"] == auth.created_at.to_isoformat()

        assert primitive["provider_method"]["provider"] == "EMAIL"
        assert primitive["provider_method"]["provider_id"] is None

    def test_should_convert_oauth_auth_to_primitive(self):
        auth = create_oauth_auth()

        primitive = auth.to_primitive()

        assert primitive["id"] == AUTH_ID
        assert primitive["user_id"] == USER_ID
        assert primitive["email"] is None

        assert primitive["provider_method"]["provider"] == "GOOGLE"
        assert (
            primitive["provider_method"]["provider_id"]
            == GOOGLE_PROVIDER_ID
        )

    def test_should_recreate_email_auth_from_primitive(self):
        auth = create_email_auth()

        primitive = auth.to_primitive()

        recreated_auth = Auth.from_primitive(primitive)

        assert recreated_auth == auth

    def test_should_recreate_oauth_auth_from_primitive(self):
        auth = create_oauth_auth()

        primitive = auth.to_primitive()

        recreated_auth = Auth.from_primitive(primitive)

        assert recreated_auth == auth

    def test_should_preserve_auth_id_when_recreating(self):
        auth = create_email_auth()

        primitive = auth.to_primitive()
        recreated_auth = Auth.from_primitive(primitive)

        assert recreated_auth.id.value == AUTH_ID

    def test_should_preserve_created_at_when_recreating(self):
        auth = create_email_auth()

        primitive = auth.to_primitive()
        recreated_auth = Auth.from_primitive(primitive)

        assert recreated_auth.created_at == auth.created_at

    def test_should_be_immutable(self):
        auth = create_email_auth()

        with pytest.raises(FrozenInstanceError):
            auth.email = None
