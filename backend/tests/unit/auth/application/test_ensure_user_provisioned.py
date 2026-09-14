import pytest

from core.auth.application.application_error import InvalidAuthCredentialsError
from core.auth.application.ensure_user_provisioned import EnsureUserProvisioned
from core.auth.domain.auth import Auth
from core.auth.domain.auth_provider import AuthProvider
from core.auth.domain.auth_repo import AuthIdentity
from core.user.domain.user import User
from tests.unit.auth.application.fake_auth_repo import FakeAuthRepo

AUTH_ID = "660e8400-e29b-41d4-a716-446655440000"
EMAIL = "test@example.com"


class TestEnsureUserProvisioned:
    def setup_method(self):
        self.repo = FakeAuthRepo()
        self.use_case = EnsureUserProvisioned(self.repo)

    def test_rejects_empty_email(self):
        with pytest.raises(InvalidAuthCredentialsError):
            self.use_case.execute(AUTH_ID, "   ")

        assert self.repo.identity_lookups == []
        assert self.repo.auths == []

    def test_rejects_missing_identity(self):
        with pytest.raises(InvalidAuthCredentialsError):
            self.use_case.execute(AUTH_ID, EMAIL)

        assert self.repo.auths == []
        assert self.repo.identity_lookups == [AUTH_ID]

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
        assert self.repo.identity_lookups == []

    def test_dispatches_email_identity_to_register_with_email(self):
        self.repo.identity = AuthIdentity(
            id=AUTH_ID,
            provider=AuthProvider.EMAIL,
            provider_id=None,
            email=EMAIL,
        )

        result = self.use_case.execute(AUTH_ID, "TEST@EXAMPLE.COM")

        assert result.provider_method.provider is AuthProvider.EMAIL
        assert result.email.value == "test@example.com"
        assert self.repo.identity_lookups == [AUTH_ID]

    def test_dispatches_google_identity_to_provision_oauth_user(self):
        self.repo.identity = AuthIdentity(
            id=AUTH_ID,
            provider=AuthProvider.GOOGLE,
            provider_id="google-123",
            email=EMAIL,
        )

        result = self.use_case.execute(AUTH_ID, EMAIL)

        assert result.provider_method.provider is AuthProvider.GOOGLE
        assert result.provider_method.provider_id.value == "google-123"
        assert self.repo.identity_lookups == [AUTH_ID]
