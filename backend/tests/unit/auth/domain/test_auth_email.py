import pytest

from core.auth.domain.auth_email import AuthEmail
from core.auth.domain.auth_error import InvalidEmailError


class TestAuthEmail:

    def test_should_create_valid_email(self):
        email = AuthEmail("test@example.com")

        assert email.value == "test@example.com"

    def test_should_normalize_email_to_lowercase(self):
        email = AuthEmail("TEST@EXAMPLE.COM")

        assert email.value == "test@example.com"

    def test_should_accept_email_with_numbers(self):
        email = AuthEmail("test123@example.com")

        assert email.value == "test123@example.com"

    def test_should_accept_email_with_dot(self):
        email = AuthEmail("john.doe@example.com")

        assert email.value == "john.doe@example.com"

    def test_should_accept_email_with_plus(self):
        email = AuthEmail("john+test@example.com")

        assert email.value == "john+test@example.com"

    def test_should_reject_invalid_email(self):
        with pytest.raises(InvalidEmailError):
            AuthEmail("invalid-email")

    def test_should_reject_email_without_at(self):
        with pytest.raises(InvalidEmailError):
            AuthEmail("test.example.com")

    def test_should_reject_email_without_domain(self):
        with pytest.raises(InvalidEmailError):
            AuthEmail("test@")

    def test_should_reject_email_without_tld(self):
        with pytest.raises(InvalidEmailError):
            AuthEmail("test@example")

    def test_should_reject_empty_email(self):
        with pytest.raises(InvalidEmailError):
            AuthEmail("")

    def test_should_reject_email_with_spaces(self):
        with pytest.raises(InvalidEmailError):
            AuthEmail("test @example.com")