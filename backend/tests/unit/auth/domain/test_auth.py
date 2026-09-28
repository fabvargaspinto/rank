from dataclasses import FrozenInstanceError

import pytest

from core.auth.domain.auth import Auth
from core.auth.domain.auth_email import AuthEmail
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


def create_oauth_auth(email: str = EMAIL) -> Auth:
    return Auth.create_with_oauth(
        id=AUTH_ID,
        user_id=USER_ID,
        provider=AuthProvider.GOOGLE,
        provider_id=GOOGLE_PROVIDER_ID,
        email=email,
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
        assert auth.email.value == EMAIL
        assert auth.created_at is not None

        assert auth.provider_method.provider == AuthProvider.GOOGLE
        assert auth.provider_method.provider_id.value == GOOGLE_PROVIDER_ID

    def test_should_create_auth_with_oauth_provider(self):
        auth = create_oauth_auth()

        assert auth.provider_method == AuthMethod.oauth(
            provider=AuthProvider.GOOGLE,
            provider_id=GOOGLE_PROVIDER_ID,
        )

    def test_should_be_immutable(self):
        auth = create_email_auth()

        with pytest.raises(FrozenInstanceError):
            auth.email = AuthEmail("otro@example.com")
