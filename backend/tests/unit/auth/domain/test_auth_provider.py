import pytest

from core.auth.domain.auth_error import InvalidAuthProviderError
from core.auth.domain.auth_provider import AuthProvider


class TestAuthProvider:

    def test_should_have_email_provider(self):
        assert AuthProvider.EMAIL.value == "EMAIL"

    def test_should_have_google_provider(self):
        assert AuthProvider.GOOGLE.value == "GOOGLE"

    def test_email_should_be_email_provider(self):
        assert AuthProvider.EMAIL.is_email() is True

    def test_google_should_not_be_email_provider(self):
        assert AuthProvider.GOOGLE.is_email() is False

    def test_email_should_not_be_oauth(self):
        assert AuthProvider.EMAIL.is_oauth() is False

    def test_google_should_be_oauth(self):
        assert AuthProvider.GOOGLE.is_oauth() is True

    def test_should_create_provider_from_string(self):
        provider = AuthProvider.from_string("GOOGLE")

        assert provider == AuthProvider.GOOGLE

    def test_should_create_provider_from_lowercase_string(self):
        provider = AuthProvider.from_string("google")

        assert provider == AuthProvider.GOOGLE

    def test_should_remove_spaces_from_provider(self):
        provider = AuthProvider.from_string(" GOOGLE ")

        assert provider == AuthProvider.GOOGLE

    def test_should_reject_unknown_provider(self):
        with pytest.raises(InvalidAuthProviderError):
            AuthProvider.from_string("FACEBOOK")

    def test_should_get_all_providers(self):
        assert AuthProvider.get_all() == ["EMAIL", "GOOGLE"]
