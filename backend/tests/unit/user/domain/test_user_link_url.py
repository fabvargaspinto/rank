import pytest

from core.user.domain.user_error import InvalidUserLinkUrlError
from core.user.domain.user_link_url import UserLinkUrl


class TestUserLinkUrl:

    def test_should_create_valid_url(self):
        url = UserLinkUrl("https://example.com/profile")

        assert url.value == "https://example.com/profile"

    def test_should_reject_http_url(self):
        with pytest.raises(InvalidUserLinkUrlError):
            UserLinkUrl("http://example.com/profile")

    def test_should_reject_url_without_https(self):
        with pytest.raises(InvalidUserLinkUrlError):
            UserLinkUrl("example.com/profile")

    def test_should_reject_empty_url(self):
        with pytest.raises(InvalidUserLinkUrlError):
            UserLinkUrl("")

    def test_should_reject_url_with_only_spaces(self):
        with pytest.raises(InvalidUserLinkUrlError):
            UserLinkUrl("   ")

    def test_should_accept_url_with_exactly_2048_characters(self):
        value = "https://" + ("a" * (2048 - 8))

        url = UserLinkUrl(value)

        assert len(url.value) == 2048

    def test_should_reject_url_longer_than_2048_characters(self):
        value = "https://" + ("a" * (2049 - 8))

        with pytest.raises(InvalidUserLinkUrlError):
            UserLinkUrl(value)

    def test_should_strip_external_spaces(self):
        url = UserLinkUrl("https://example.com/profile ")

        assert url.value == "https://example.com/profile"

    def test_should_strip_leading_spaces(self):
        url = UserLinkUrl(" https://example.com/profile")

        assert url.value == "https://example.com/profile"

    def test_should_return_lowercase_host(self):
        url = UserLinkUrl("https://WWW.YouTube.com/watch?v=abc")

        assert url.host() == "www.youtube.com"
