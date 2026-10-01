import pytest

from core.auth.application.application_error import (
    EmailAlreadyExistsError,
    InvalidAuthCredentialsError,
)
from core.auth.application.provision_identity import ProvisionIdentity
from core.auth.domain.auth import Auth
from core.auth.domain.auth_email import AuthEmail
from core.auth.domain.auth_id import AuthId
from core.auth.domain.auth_provider import AuthProvider
from core.auth.domain.auth_provider_id import AuthProviderId
from core.auth.domain.auth_repo import AuthIdentity
from core.user.domain.user import User
from tests.unit.auth.application.fake_auth_repo import FakeAuthRepo

AUTH_ID = "660e8400-e29b-41d4-a716-446655440000"
OTHER_AUTH_ID = "770e8400-e29b-41d4-a716-446655440000"
EMAIL = "test@example.com"
GOOGLE_ID = "google-123"


def _email_identity(auth_id: str = AUTH_ID) -> AuthIdentity:
    return AuthIdentity(
        id=AuthId(auth_id),
        provider=AuthProvider.EMAIL,
        provider_id=None,
        email=AuthEmail(EMAIL),
    )


def _google_identity(auth_id: str = AUTH_ID) -> AuthIdentity:
    return AuthIdentity(
        id=AuthId(auth_id),
        provider=AuthProvider.GOOGLE,
        provider_id=AuthProviderId(GOOGLE_ID),
        email=AuthEmail(EMAIL),
    )


class TestProvisionIdentity:
    def setup_method(self):
        self.repo = FakeAuthRepo()
        self.use_case = ProvisionIdentity(self.repo)

    def test_rejects_empty_email(self):
        with pytest.raises(InvalidAuthCredentialsError):
            self.use_case.execute(AUTH_ID, "   ")

        assert self.repo.auths == []

    def test_rejects_missing_identity(self):
        with pytest.raises(InvalidAuthCredentialsError):
            self.use_case.execute(AUTH_ID, EMAIL)

        assert self.repo.auths == []

    def test_returns_existing_auth_by_id(self):
        user = User.create_empty()
        existing = Auth.create_with_email(
            id=AUTH_ID,
            user_id=user.id.value,
            email=EMAIL,
        )
        self.repo.save(user, existing)

        result = self.use_case.execute(AUTH_ID, EMAIL)

        assert result is existing
        assert len(self.repo.users) == 1

    def test_provisions_email_identity(self):
        self.repo.identity = _email_identity()

        result = self.use_case.execute(AUTH_ID, "TEST@EXAMPLE.COM")

        assert result.email.value == "test@example.com"
        assert result.provider_method.provider is AuthProvider.EMAIL
        assert self.repo.find_by_email("test@example.com") is result
        assert len(self.repo.users) == 1

    def test_provisions_google_identity(self):
        self.repo.identity = _google_identity()

        result = self.use_case.execute(AUTH_ID, EMAIL)

        assert result.provider_method.provider is AuthProvider.GOOGLE
        assert result.provider_method.provider_id.value == GOOGLE_ID
        assert self.repo.find_by_provider_id(AuthProvider.GOOGLE, GOOGLE_ID) is result

    def test_returns_existing_google_identity(self):
        user = User.create_empty()
        existing = Auth.create_with_oauth(
            id=OTHER_AUTH_ID,
            user_id=user.id.value,
            provider=AuthProvider.GOOGLE,
            provider_id=GOOGLE_ID,
            email="other@example.com",
        )
        self.repo.save(user, existing)
        self.repo.identity = _google_identity()

        result = self.use_case.execute(AUTH_ID, EMAIL)

        assert result is existing
        assert len(self.repo.users) == 1

    def test_rejects_duplicate_email(self):
        user = User.create_empty()
        existing = Auth.create_with_email(
            id=OTHER_AUTH_ID,
            user_id=user.id.value,
            email=EMAIL,
        )
        self.repo.save(user, existing)
        self.repo.identity = _email_identity()

        with pytest.raises(EmailAlreadyExistsError):
            self.use_case.execute(AUTH_ID, "TEST@EXAMPLE.COM")

        assert self.repo.find_by_id(AUTH_ID) is None

    def test_save_failure_does_not_persist(self):
        self.repo.identity = _email_identity()
        self.repo.fail_on_save = True

        with pytest.raises(EmailAlreadyExistsError):
            self.use_case.execute(AUTH_ID, EMAIL)

        assert self.repo.auths == []
        assert self.repo.users == []

    def test_rejects_google_identity_without_provider_id(self):
        self.repo.identity = AuthIdentity(
            id=AuthId(AUTH_ID),
            provider=AuthProvider.GOOGLE,
            provider_id=None,
            email=AuthEmail(EMAIL),
        )

        with pytest.raises(InvalidAuthCredentialsError):
            self.use_case.execute(AUTH_ID, EMAIL)

        assert self.repo.auths == []
