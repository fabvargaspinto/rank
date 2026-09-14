import pytest

from core.auth.application.application_error import (
    EmailAlreadyExistsError,
    InvalidAuthCredentialsError,
)
from core.auth.application.ensure_user_provisioned import EnsureUserProvisioned
from core.auth.domain.auth import Auth
from core.auth.domain.auth_provider import AuthProvider
from core.auth.domain.auth_repo import AuthIdentity
from core.user.domain.user import User
from tests.unit.auth.application.fake_auth_repo import FakeAuthRepo

AUTH_ID = "660e8400-e29b-41d4-a716-446655440000"
OTHER_AUTH_ID = "770e8400-e29b-41d4-a716-446655440000"
EMAIL = "test@example.com"


class TestEnsureUserProvisioned:
    def setup_method(self):
        self.repo = FakeAuthRepo()
        self.use_case = EnsureUserProvisioned(self.repo)

    def test_rejects_missing_identity(self):
        with pytest.raises(InvalidAuthCredentialsError):
            self.use_case.execute(AUTH_ID, EMAIL)

        assert self.repo.auths == []
        assert self.repo.users == []
        assert self.repo.identity_lookups == [AUTH_ID]

    def test_rejects_empty_email(self):
        self.repo.identity = AuthIdentity(
            id=AUTH_ID,
            provider=AuthProvider.EMAIL,
            provider_id=None,
            email=EMAIL,
        )

        with pytest.raises(InvalidAuthCredentialsError):
            self.use_case.execute(AUTH_ID, "   ")

        assert self.repo.auths == []
        assert self.repo.identity_lookups == []

    def test_rejects_oauth_identity_without_provider_id(self):
        self.repo.identity = AuthIdentity(
            id=AUTH_ID,
            provider=AuthProvider.GOOGLE,
            provider_id=None,
            email=EMAIL,
        )

        with pytest.raises(InvalidAuthCredentialsError):
            self.use_case.execute(AUTH_ID, EMAIL)

        assert self.repo.auths == []

    def test_provisions_email_identity(self):
        self.repo.identity = AuthIdentity(
            id=AUTH_ID,
            provider=AuthProvider.EMAIL,
            provider_id=None,
            email="ignored@example.com",
        )

        result = self.use_case.execute(AUTH_ID, "TEST@EXAMPLE.COM")

        assert result.id.value == AUTH_ID
        assert result.email.value == "test@example.com"
        assert result.provider_method.provider is AuthProvider.EMAIL
        assert self.repo.find_by_email("test@example.com") == result
        assert len(self.repo.users) == 1
        assert result.user_id.value == self.repo.users[0].id.value

    def test_provisions_google_identity(self):
        self.repo.identity = AuthIdentity(
            id=AUTH_ID,
            provider=AuthProvider.GOOGLE,
            provider_id="google-123",
            email="ignored@example.com",
        )

        result = self.use_case.execute(AUTH_ID, "TEST@EXAMPLE.COM")

        assert result.id.value == AUTH_ID
        assert result.email.value == "test@example.com"
        assert result.provider_method.provider is AuthProvider.GOOGLE
        assert result.provider_method.provider_id.value == "google-123"
        assert self.repo.find_by_provider_id(
            AuthProvider.GOOGLE,
            "google-123",
        ) == result
        assert len(self.repo.users) == 1

    def test_returns_existing_auth_by_id_without_identity_lookup(self):
        existing_user = User.create_empty()
        existing = Auth.create_with_email(
            id=AUTH_ID,
            user_id=existing_user.id.value,
            email=EMAIL,
        )
        self.repo.save(existing_user, existing)

        result = self.use_case.execute(AUTH_ID, EMAIL)

        assert result is existing
        assert len(self.repo.auths) == 1
        assert len(self.repo.users) == 1
        assert self.repo.identity_lookups == []

    def test_returns_existing_oauth_auth_by_provider_id(self):
        existing_user = User.create_empty()
        existing = Auth.create_with_oauth(
            id=OTHER_AUTH_ID,
            user_id=existing_user.id.value,
            provider=AuthProvider.GOOGLE,
            provider_id="google-123",
            email="other@example.com",
        )
        self.repo.save(existing_user, existing)
        self.repo.identity = AuthIdentity(
            id=AUTH_ID,
            provider=AuthProvider.GOOGLE,
            provider_id="google-123",
            email=EMAIL,
        )

        result = self.use_case.execute(AUTH_ID, EMAIL)

        assert result is existing
        assert len(self.repo.auths) == 1

    def test_rejects_email_already_linked_to_another_auth(self):
        existing_user = User.create_empty()
        existing = Auth.create_with_email(
            id=OTHER_AUTH_ID,
            user_id=existing_user.id.value,
            email=EMAIL,
        )
        self.repo.save(existing_user, existing)
        self.repo.identity = AuthIdentity(
            id=AUTH_ID,
            provider=AuthProvider.EMAIL,
            provider_id=None,
            email=EMAIL,
        )

        with pytest.raises(EmailAlreadyExistsError):
            self.use_case.execute(AUTH_ID, "TEST@EXAMPLE.COM")

        assert self.repo.auths == [existing]

    def test_rejects_oauth_when_email_already_registered(self):
        existing_user = User.create_empty()
        existing = Auth.create_with_email(
            id=OTHER_AUTH_ID,
            user_id=existing_user.id.value,
            email=EMAIL,
        )
        self.repo.save(existing_user, existing)
        self.repo.identity = AuthIdentity(
            id=AUTH_ID,
            provider=AuthProvider.GOOGLE,
            provider_id="google-123",
            email=EMAIL,
        )

        with pytest.raises(EmailAlreadyExistsError):
            self.use_case.execute(AUTH_ID, EMAIL)

        assert self.repo.auths == [existing]
