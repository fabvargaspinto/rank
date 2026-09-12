import pytest

from core.user.domain.user_avatar import UserAvatar
from core.user.domain.user_error import InvalidUserAvatarError


class TestUserAvatar:

    def test_should_create_valid_avatar(self):
        avatar = UserAvatar("https://example.com/avatar.jpg")

        assert avatar.value == "https://example.com/avatar.jpg"

    def test_should_accept_http_url(self):
        with pytest.raises(InvalidUserAvatarError):
            UserAvatar("http://example.com/avatar.jpg")

    def test_should_reject_url_without_https(self):
        with pytest.raises(InvalidUserAvatarError):
            UserAvatar("example.com/avatar.jpg")

    def test_should_reject_empty_url(self):
        with pytest.raises(InvalidUserAvatarError):
            UserAvatar("")

    def test_should_strip_external_spaces(self):
        avatar = UserAvatar("https://example.com/avatar.jpg ")

        assert avatar.value == "https://example.com/avatar.jpg"

    def test_should_strip_leading_spaces(self):
        avatar = UserAvatar(" https://example.com/avatar.jpg")

        assert avatar.value == "https://example.com/avatar.jpg"

