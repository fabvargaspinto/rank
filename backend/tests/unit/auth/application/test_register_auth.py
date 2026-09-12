
import pytest
from unittest.mock import Mock

from core.auth.application.register_auth import RegisterAuth
from core.auth.application.application_error import (
    EmailAlreadyExistsError,
    InvalidAuthCredentialsError,
    InvalidAuthProviderError,
    PasswordMismatchError,
)
from core.auth.domain.auth_error import InvalidAuthPasswordError
from core.auth.domain.auth_provider import AuthProvider
from core.auth.domain.auth_repo import OAuthIdentity
from core.auth.infrastructure.error_infrastructure import IdentityAlreadyExistsError


AUTH_ID = "660e8400-e29b-41d4-a716-446655440000"


class TestRegisterAuth:

    def setup_method(self):
        self.auth_repo = Mock()
        self.auth_repo.find_by_email.return_value = None
        self.auth_repo.find_by_provider_id.return_value = None
        self.auth_repo.get_oauth_identity.return_value = None
        self.auth_repo.create_identity.return_value = AUTH_ID
        self.register_auth = RegisterAuth(self.auth_repo)

    # ---------------------------------------------------------
    # WITH EMAIL
    # ---------------------------------------------------------

    def test_should_register_with_email(self):
        self.auth_repo.save.return_value = "saved"

        result = self.register_auth.with_email(
            email="TEST@EXAMPLE.COM",
            password="Password123",
            confirm_password="Password123",
        )

        assert result == "saved"

        self.auth_repo.find_by_email.assert_called_once_with(
            "test@example.com"
        )
        self.auth_repo.create_identity.assert_called_once_with(
            "test@example.com",
            "Password123",
        )
        self.auth_repo.delete_identity.assert_not_called()

        saved_auth = self.auth_repo.save.call_args.kwargs["auth"]
        saved_user = self.auth_repo.save.call_args.kwargs["user"]
        assert saved_auth.id.value == AUTH_ID
        assert saved_auth.email.value == "test@example.com"
        assert saved_auth.provider_method.provider == AuthProvider.EMAIL
        assert saved_user.id.value == saved_auth.user_id.value

    def test_should_reject_when_passwords_do_not_match(self):
        with pytest.raises(PasswordMismatchError):
            self.register_auth.with_email(
                email="test@example.com",
                password="Password123",
                confirm_password="Password456",
            )

        self.auth_repo.find_by_email.assert_not_called()
        self.auth_repo.create_identity.assert_not_called()
        self.auth_repo.save.assert_not_called()

    def test_should_reject_invalid_password(self):
        with pytest.raises(InvalidAuthPasswordError):
            self.register_auth.with_email(
                email="test@example.com",
                password="short",
                confirm_password="short",
            )

        self.auth_repo.find_by_email.assert_not_called()
        self.auth_repo.create_identity.assert_not_called()
        self.auth_repo.save.assert_not_called()

    def test_should_reject_existing_email(self):
        self.auth_repo.find_by_email.return_value = Mock()

        with pytest.raises(EmailAlreadyExistsError):
            self.register_auth.with_email(
                email="test@example.com",
                password="Password123",
                confirm_password="Password123",
            )

        self.auth_repo.find_by_email.assert_called_once_with(
            "test@example.com"
        )
        self.auth_repo.create_identity.assert_not_called()
        self.auth_repo.save.assert_not_called()

    def test_should_map_duplicate_identity_to_email_already_exists(self):
        self.auth_repo.create_identity.side_effect = IdentityAlreadyExistsError(
            "duplicate"
        )

        with pytest.raises(EmailAlreadyExistsError):
            self.register_auth.with_email(
                email="test@example.com",
                password="Password123",
                confirm_password="Password123",
            )

        self.auth_repo.save.assert_not_called()
        self.auth_repo.delete_identity.assert_not_called()

    def test_should_delete_identity_when_save_fails(self):
        self.auth_repo.save.side_effect = RuntimeError("db")

        with pytest.raises(RuntimeError):
            self.register_auth.with_email(
                email="test@example.com",
                password="Password123",
                confirm_password="Password123",
            )

        self.auth_repo.delete_identity.assert_called_once_with(AUTH_ID)

    # ---------------------------------------------------------
    # WITH OAUTH
    # ---------------------------------------------------------

    def test_should_register_with_oauth(self):
        self.auth_repo.save.return_value = "saved"

        result = self.register_auth.with_oauth(
            id=AUTH_ID,
            provider=AuthProvider.GOOGLE,
            provider_id="google-123",
            email="TEST@EXAMPLE.COM",
        )

        assert result == "saved"

        self.auth_repo.find_by_provider_id.assert_called_once_with(
            AuthProvider.GOOGLE,
            "google-123",
        )
        self.auth_repo.find_by_email.assert_called_once_with(
            "test@example.com"
        )

        saved_auth = self.auth_repo.save.call_args.kwargs["auth"]
        assert saved_auth.id.value == AUTH_ID
        assert saved_auth.email.value == "test@example.com"
        assert saved_auth.provider_method.provider == AuthProvider.GOOGLE

    def test_should_return_existing_oauth_auth(self):
        existing = Mock()
        self.auth_repo.find_by_provider_id.return_value = existing

        result = self.register_auth.with_oauth(
            id=AUTH_ID,
            provider=AuthProvider.GOOGLE,
            provider_id="google-123",
            email="test@example.com",
        )

        assert result is existing
        self.auth_repo.find_by_email.assert_not_called()
        self.auth_repo.save.assert_not_called()

    def test_should_reject_oauth_without_email(self):
        with pytest.raises(InvalidAuthCredentialsError):
            self.register_auth.with_oauth(
                id=AUTH_ID,
                provider=AuthProvider.GOOGLE,
                provider_id="google-123",
            )

        self.auth_repo.find_by_email.assert_not_called()
        self.auth_repo.save.assert_not_called()

    def test_should_reject_email_provider_when_registering_with_oauth(self):
        with pytest.raises(InvalidAuthProviderError):
            self.register_auth.with_oauth(
                id=AUTH_ID,
                provider=AuthProvider.EMAIL,
                provider_id="email-123",
                email="test@example.com",
            )

        self.auth_repo.find_by_email.assert_not_called()
        self.auth_repo.save.assert_not_called()

    def test_should_reject_existing_email_when_registering_with_oauth(self):
        self.auth_repo.find_by_email.return_value = Mock()

        with pytest.raises(EmailAlreadyExistsError):
            self.register_auth.with_oauth(
                id=AUTH_ID,
                provider=AuthProvider.GOOGLE,
                provider_id="google-123",
                email="test@example.com",
            )

        self.auth_repo.find_by_email.assert_called_once_with(
            "test@example.com"
        )
        self.auth_repo.save.assert_not_called()

    def test_should_register_from_oauth_token(self):
        self.auth_repo.get_oauth_identity.return_value = OAuthIdentity(
            id=AUTH_ID,
            provider=AuthProvider.GOOGLE,
            provider_id="google-123",
            email="test@example.com",
        )
        self.auth_repo.save.return_value = "saved"

        result = self.register_auth.with_oauth_token("token")

        assert result == "saved"
        self.auth_repo.get_oauth_identity.assert_called_once_with("token")
        saved_auth = self.auth_repo.save.call_args.kwargs["auth"]
        assert saved_auth.id.value == AUTH_ID

    def test_should_reject_invalid_oauth_token(self):
        with pytest.raises(InvalidAuthCredentialsError):
            self.register_auth.with_oauth_token("bad-token")

        self.auth_repo.save.assert_not_called()
