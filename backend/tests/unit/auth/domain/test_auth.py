from dataclasses import FrozenInstanceError

import pytest

from core.auth.domain.auth import Auth
from core.auth.domain.auth_method import AuthMethod
from core.auth.domain.auth_provider import AuthProvider


USER_ID = "550e8400-e29b-41d4-a716-446655440000"
EMAIL = "test@example.com"
GOOGLE_PROVIDER_ID = "google-user-123"


class TestAuth:

    def test_should_create_auth_with_email(self):
        auth = Auth.create_with_email(
            user_id=USER_ID,
            email=EMAIL,
        )

        assert auth.id is not None
        assert auth.user_id.value == USER_ID
        assert auth.email.value == EMAIL
        assert auth.created_at is not None

        assert auth.provider_method.provider == AuthProvider.EMAIL
        assert auth.provider_method.provider_id is None

    def test_should_normalize_email_when_creating_auth(self):
        auth = Auth.create_with_email(
            user_id=USER_ID,
            email="TEST@EXAMPLE.COM",
        )

        assert auth.email.value == "test@example.com"

    def test_should_create_auth_with_google(self):
        auth = Auth.create_with_oauth(
            user_id=USER_ID,
            provider=AuthProvider.GOOGLE,
            provider_id=GOOGLE_PROVIDER_ID,
        )

        assert auth.id is not None
        assert auth.user_id.value == USER_ID
        assert auth.email is None
        assert auth.created_at is not None

        assert auth.provider_method.provider == AuthProvider.GOOGLE
        assert auth.provider_method.provider_id.value == GOOGLE_PROVIDER_ID

    def test_should_create_auth_with_oauth_provider(self):
        auth = Auth.create_with_oauth(
            user_id=USER_ID,
            provider=AuthProvider.GOOGLE,
            provider_id=GOOGLE_PROVIDER_ID,
        )

        assert auth.provider_method == AuthMethod.oauth(
            provider=AuthProvider.GOOGLE,
            provider_id=GOOGLE_PROVIDER_ID,
        )

    def test_should_convert_email_auth_to_primitive(self):
        auth = Auth.create_with_email(
            user_id=USER_ID,
            email=EMAIL,
        )

        primitive = auth.to_primitive()

        assert primitive["id"] == auth.id.value
        assert primitive["user_id"] == USER_ID
        assert primitive["email"] == EMAIL
        assert primitive["created_at"] == auth.created_at.to_isoformat()

        assert primitive["provider_method"]["provider"] == "EMAIL"
        assert primitive["provider_method"]["provider_id"] is None

    def test_should_convert_oauth_auth_to_primitive(self):
        auth = Auth.create_with_oauth(
            user_id=USER_ID,
            provider=AuthProvider.GOOGLE,
            provider_id=GOOGLE_PROVIDER_ID,
        )

        primitive = auth.to_primitive()

        assert primitive["id"] == auth.id.value
        assert primitive["user_id"] == USER_ID
        assert primitive["email"] is None

        assert primitive["provider_method"]["provider"] == "GOOGLE"
        assert (
            primitive["provider_method"]["provider_id"]
            == GOOGLE_PROVIDER_ID
        )

    def test_should_recreate_email_auth_from_primitive(self):
        auth = Auth.create_with_email(
            user_id=USER_ID,
            email=EMAIL,
        )

        primitive = auth.to_primitive()

        recreated_auth = Auth.from_primitive(primitive)

        assert recreated_auth == auth

    def test_should_recreate_oauth_auth_from_primitive(self):
        auth = Auth.create_with_oauth(
            user_id=USER_ID,
            provider=AuthProvider.GOOGLE,
            provider_id=GOOGLE_PROVIDER_ID,
        )

        primitive = auth.to_primitive()

        recreated_auth = Auth.from_primitive(primitive)

        assert recreated_auth == auth

    def test_should_preserve_auth_id_when_recreating(self):
        auth = Auth.create_with_email(
            user_id=USER_ID,
            email=EMAIL,
        )

        primitive = auth.to_primitive()
        recreated_auth = Auth.from_primitive(primitive)

        assert recreated_auth.id == auth.id

    def test_should_preserve_created_at_when_recreating(self):
        auth = Auth.create_with_email(
            user_id=USER_ID,
            email=EMAIL,
        )

        primitive = auth.to_primitive()
        recreated_auth = Auth.from_primitive(primitive)

        assert recreated_auth.created_at == auth.created_at

    def test_should_be_immutable(self):
        auth = Auth.create_with_email(
            user_id=USER_ID,
            email=EMAIL,
        )

        with pytest.raises(FrozenInstanceError):
            auth.email = None   