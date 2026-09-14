import pytest

from core.auth.application.application_error import (
    EmailAlreadyExistsError,
    InvalidAuthCredentialsError,
)
from core.auth.application.register_with_email import RegisterWithEmail
from core.auth.domain.auth import Auth
from core.user.domain.user import User
from tests.unit.auth.application.fake_auth_repo import FakeAuthRepo

AUTH_ID = "660e8400-e29b-41d4-a716-446655440000"
OTHER_AUTH_ID = "770e8400-e29b-41d4-a716-446655440000"
EMAIL = "test@example.com"


class TestRegisterWithEmail:
    def setup_method(self):
        self.repo = FakeAuthRepo()
        self.use_case = RegisterWithEmail(self.repo)

    def test_rejects_empty_email(self):
        with pytest.raises(InvalidAuthCredentialsError):
            self.use_case.execute(AUTH_ID, "   ")

        assert self.repo.auths == []

    def test_provisions_email_identity(self):
        result = self.use_case.execute(AUTH_ID, "TEST@EXAMPLE.COM")

        assert result.id.value == AUTH_ID
        assert result.email.value == "test@example.com"
        assert result.provider_method.provider.is_email()
        assert self.repo.find_by_email("test@example.com") == result
        assert len(self.repo.users) == 1
        assert result.user_id.value == self.repo.users[0].id.value

    def test_returns_existing_auth_by_id(self):
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

    def test_rejects_email_already_linked_to_another_auth(self):
        existing_user = User.create_empty()
        existing = Auth.create_with_email(
            id=OTHER_AUTH_ID,
            user_id=existing_user.id.value,
            email=EMAIL,
        )
        self.repo.save(existing_user, existing)

        with pytest.raises(EmailAlreadyExistsError):
            self.use_case.execute(AUTH_ID, "TEST@EXAMPLE.COM")

        assert self.repo.auths == [existing]
