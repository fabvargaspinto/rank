import pytest

from core.auth.application.application_error import (
    EmailAlreadyExistsError,
    InvalidAuthCredentialsError,
)
from core.auth.application.register_with_email import RegisterWithEmail
from core.auth.domain.auth import Auth
from core.auth.domain.auth_provider import AuthProvider
from core.user.domain.user import User
from tests.unit.auth.application.fake_auth_repo import FakeAuthRepo

AUTH_ID = "660e8400-e29b-41d4-a716-446655440000"
OTHER_AUTH_ID = "770e8400-e29b-41d4-a716-446655440000"
EMAIL = "test@example.com"


def _seed_email_auth(repo: FakeAuthRepo, auth_id: str, email: str) -> Auth:
    user = User.create_empty()
    auth = Auth.create_with_email(
        id=auth_id,
        user_id=user.id.value,
        email=email,
    )
    repo.save(user, auth)
    return auth


class TestRegisterWithEmail:
    def setup_method(self):
        self.repo = FakeAuthRepo()
        self.use_case = RegisterWithEmail(self.repo)

    def test_registering_creates_a_user_and_an_email_identity(self):
        result = self.use_case.execute(AUTH_ID, "TEST@EXAMPLE.COM")

        assert self.repo.find_by_email("test@example.com") == result
        assert result.id.value == AUTH_ID
        assert len(self.repo.users) == 1
        assert result.user_id.value == self.repo.users[0].id.value
        assert result.provider_method.provider is AuthProvider.EMAIL
        assert result.provider_method.provider_id is None

    def test_normalizes_email(self):
        result = self.use_case.execute(AUTH_ID, "TEST@EXAMPLE.COM")

        assert result.email.value == "test@example.com"

    def test_rejects_empty_email(self):
        with pytest.raises(InvalidAuthCredentialsError):
            self.use_case.execute(AUTH_ID, "   ")

        assert self.repo.auths == []
        assert self.repo.users == []

    def test_returns_existing_auth_by_id(self):
        existing = _seed_email_auth(self.repo, AUTH_ID, EMAIL)

        result = self.use_case.execute(AUTH_ID, EMAIL)

        assert result is existing
        assert self.repo.auths == [existing]
        assert len(self.repo.users) == 1

    def test_rejects_duplicate_email(self):
        existing = _seed_email_auth(self.repo, OTHER_AUTH_ID, EMAIL)

        with pytest.raises(EmailAlreadyExistsError):
            self.use_case.execute(AUTH_ID, "TEST@EXAMPLE.COM")

        assert self.repo.auths == [existing]
        assert len(self.repo.users) == 1

    def test_save_failure_does_not_persist_user_or_identity(self):
        self.repo.fail_on_save = True

        with pytest.raises(EmailAlreadyExistsError):
            self.use_case.execute(AUTH_ID, EMAIL)

        assert self.repo.auths == []
        assert self.repo.users == []
        assert self.repo.find_by_email(EMAIL) is None
