

import pytest
from unittest.mock import Mock

from core.auth.application.register_auth import RegisterAuth
from core.auth.application.application_error import (
    EmailAlreadyExistsError,
    PasswordMismatchError,
    InvalidAuthProviderError,
)
from core.auth.domain.auth_provider import AuthProvider


class TestRegisterAuth:

    def setup_method(self):
        self.auth_repo = Mock()
        self.register_auth = RegisterAuth(self.auth_repo)

    # ---------------------------------------------------------
    # WITH EMAIL
    # ---------------------------------------------------------

    def test_should_register_with_email(self):
        self.auth_repo.find_by_email.return_value = None
        self.auth_repo.save.return_value = "saved"

        result = self.register_auth.with_email(
            provider=AuthProvider.EMAIL,
            email="test@example.com",
            password="Password123",
            confirm_password="Password123",
        )

        assert result == "saved"

        self.auth_repo.find_by_email.assert_called_once_with(
            "test@example.com"
        )

        self.auth_repo.save.assert_called_once()

    def test_should_reject_oauth_provider_when_registering_with_email(self):
        with pytest.raises(InvalidAuthProviderError):
            self.register_auth.with_email(
                provider=AuthProvider.GOOGLE,
                email="test@example.com",
                password="Password123",
                confirm_password="Password123",
            )

        self.auth_repo.find_by_email.assert_not_called()
        self.auth_repo.save.assert_not_called()

    def test_should_reject_when_passwords_do_not_match(self):
        with pytest.raises(PasswordMismatchError):
            self.register_auth.with_email(
                provider=AuthProvider.EMAIL,
                email="test@example.com",
                password="Password123",
                confirm_password="Password456",
            )

        self.auth_repo.find_by_email.assert_not_called()
        self.auth_repo.save.assert_not_called()

    def test_should_reject_existing_email(self):
        existing_auth = Mock()

        self.auth_repo.find_by_email.return_value = existing_auth

        with pytest.raises(EmailAlreadyExistsError):
            self.register_auth.with_email(
                provider=AuthProvider.EMAIL,
                email="test@example.com",
                password="Password123",
                confirm_password="Password123",
            )

        self.auth_repo.find_by_email.assert_called_once_with(
            "test@example.com"
        )

        self.auth_repo.save.assert_not_called()

    # ---------------------------------------------------------
    # WITH OAUTH
    # ---------------------------------------------------------

    def test_should_register_with_oauth(self):
        self.auth_repo.find_by_email.return_value = None
        self.auth_repo.save.return_value = "saved"

        result = self.register_auth.with_oauth(
            provider=AuthProvider.GOOGLE,
            provider_id="google-123",
            email="test@example.com",
        )

        assert result == "saved"

        self.auth_repo.find_by_email.assert_called_once_with(
            "test@example.com"
        )

        self.auth_repo.save.assert_called_once()

    def test_should_register_oauth_without_email(self):
        self.auth_repo.save.return_value = "saved"

        result = self.register_auth.with_oauth(
            provider=AuthProvider.GOOGLE,
            provider_id="google-123",
        )

        assert result == "saved"

        self.auth_repo.find_by_email.assert_not_called()
        self.auth_repo.save.assert_called_once()

    def test_should_reject_email_provider_when_registering_with_oauth(self):
        with pytest.raises(InvalidAuthProviderError):
            self.register_auth.with_oauth(
                provider=AuthProvider.EMAIL,
                provider_id="email-123",
                email="test@example.com",
            )

        self.auth_repo.find_by_email.assert_not_called()
        self.auth_repo.save.assert_not_called()

    def test_should_reject_existing_email_when_registering_with_oauth(self):
        existing_auth = Mock()

        self.auth_repo.find_by_email.return_value = existing_auth

        with pytest.raises(EmailAlreadyExistsError):
            self.register_auth.with_oauth(
                provider=AuthProvider.GOOGLE,
                provider_id="google-123",
                email="test@example.com",
            )

        self.auth_repo.find_by_email.assert_called_once_with(
            "test@example.com"
        )

        self.auth_repo.save.assert_not_called()