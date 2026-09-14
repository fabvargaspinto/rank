import pytest

from core.auth.application.application_error import (
    EmailAlreadyExistsError,
    InvalidAuthCredentialsError,
    InvalidAuthProviderError,
)
from core.auth.application.provision_oauth_user import ProvisionOAuthUser
from core.auth.domain.auth import Auth
from core.auth.domain.auth_provider import AuthProvider
from core.user.domain.user import User
from tests.unit.auth.application.fake_auth_repo import FakeAuthRepo

AUTH_ID = "660e8400-e29b-41d4-a716-446655440000"
OTHER_AUTH_ID = "770e8400-e29b-41d4-a716-446655440000"
EMAIL = "test@example.com"
GOOGLE_ID = "google-123"


class TestProvisionOAuthUser:
    def setup_method(self):
        self.repo = FakeAuthRepo()
        self.use_case = ProvisionOAuthUser(self.repo)

    def test_rejects_empty_email(self):
        with pytest.raises(InvalidAuthCredentialsError):
            self.use_case.execute(AUTH_ID, "   ", AuthProvider.GOOGLE, GOOGLE_ID)

        assert self.repo.auths == []

    def test_rejects_email_provider(self):
        with pytest.raises(InvalidAuthProviderError):
            self.use_case.execute(AUTH_ID, EMAIL, AuthProvider.EMAIL, None)

        assert self.repo.auths == []

    def test_rejects_oauth_without_provider_id(self):
        with pytest.raises(InvalidAuthCredentialsError):
            self.use_case.execute(AUTH_ID, EMAIL, AuthProvider.GOOGLE, None)

        assert self.repo.auths == []

    def test_provisions_google_identity(self):
        result = self.use_case.execute(
            AUTH_ID,
            "TEST@EXAMPLE.COM",
            AuthProvider.GOOGLE,
            GOOGLE_ID,
        )

        assert result.id.value == AUTH_ID
        assert result.email.value == "test@example.com"
        assert result.provider_method.provider is AuthProvider.GOOGLE
        assert result.provider_method.provider_id.value == GOOGLE_ID
        assert self.repo.find_by_provider_id(AuthProvider.GOOGLE, GOOGLE_ID) == result
        assert len(self.repo.users) == 1

    def test_returns_existing_auth_by_id(self):
        existing_user = User.create_empty()
        existing = Auth.create_with_oauth(
            id=AUTH_ID,
            user_id=existing_user.id.value,
            provider=AuthProvider.GOOGLE,
            provider_id=GOOGLE_ID,
            email=EMAIL,
        )
        self.repo.save(existing_user, existing)

        result = self.use_case.execute(
            AUTH_ID,
            EMAIL,
            AuthProvider.GOOGLE,
            GOOGLE_ID,
        )

        assert result is existing
        assert len(self.repo.auths) == 1

    def test_returns_existing_auth_by_provider_id(self):
        existing_user = User.create_empty()
        existing = Auth.create_with_oauth(
            id=OTHER_AUTH_ID,
            user_id=existing_user.id.value,
            provider=AuthProvider.GOOGLE,
            provider_id=GOOGLE_ID,
            email="other@example.com",
        )
        self.repo.save(existing_user, existing)

        result = self.use_case.execute(
            AUTH_ID,
            EMAIL,
            AuthProvider.GOOGLE,
            GOOGLE_ID,
        )

        assert result is existing
        assert len(self.repo.auths) == 1

    def test_rejects_when_email_already_registered(self):
        existing_user = User.create_empty()
        existing = Auth.create_with_email(
            id=OTHER_AUTH_ID,
            user_id=existing_user.id.value,
            email=EMAIL,
        )
        self.repo.save(existing_user, existing)

        with pytest.raises(EmailAlreadyExistsError):
            self.use_case.execute(
                AUTH_ID,
                EMAIL,
                AuthProvider.GOOGLE,
                GOOGLE_ID,
            )

        assert self.repo.auths == [existing]
