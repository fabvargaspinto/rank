import pytest
from unittest.mock import Mock

from core.auth.application.login_auth import LoginAuth
from core.auth.application.application_error import (
    EmailNotFoundError,
    PasswordMismatchError,
    InvalidAuthProviderError,
)


class TestLoginAuth:

    def setup_method(self):
        self.auth_repo = Mock()
        self.auth_repo.find_by_email.return_value = None
        self.auth_repo.verify_password.return_value = True
        self.login_auth = LoginAuth(self.auth_repo)

    def test_should_login_with_email(self):
        auth = Mock()
        auth.provider_method.provider.is_oauth.return_value = False
        self.auth_repo.find_by_email.return_value = auth

        result = self.login_auth.with_email(
            email="TEST@EXAMPLE.COM",
            password="Password123",
        )

        assert result is auth

        self.auth_repo.find_by_email.assert_called_once_with(
            "test@example.com"
        )
        self.auth_repo.verify_password.assert_called_once_with(
            "test@example.com",
            "Password123",
        )

    def test_should_raise_error_when_email_does_not_exist(self):
        with pytest.raises(EmailNotFoundError):
            self.login_auth.with_email(
                email="test@example.com",
                password="Password123",
            )

        self.auth_repo.find_by_email.assert_called_once_with(
            "test@example.com"
        )
        self.auth_repo.verify_password.assert_not_called()

    def test_should_raise_error_when_password_is_incorrect(self):
        auth = Mock()
        auth.provider_method.provider.is_oauth.return_value = False
        self.auth_repo.find_by_email.return_value = auth
        self.auth_repo.verify_password.return_value = False

        with pytest.raises(PasswordMismatchError):
            self.login_auth.with_email(
                email="test@example.com",
                password="WrongPassword",
            )

        self.auth_repo.find_by_email.assert_called_once_with(
            "test@example.com"
        )
        self.auth_repo.verify_password.assert_called_once_with(
            "test@example.com",
            "WrongPassword",
        )

    def test_should_reject_oauth_account_when_logging_in_with_email(self):
        auth = Mock()
        auth.provider_method.provider.is_oauth.return_value = True
        self.auth_repo.find_by_email.return_value = auth

        with pytest.raises(InvalidAuthProviderError):
            self.login_auth.with_email(
                email="test@example.com",
                password="Password123",
            )

        self.auth_repo.verify_password.assert_not_called()
