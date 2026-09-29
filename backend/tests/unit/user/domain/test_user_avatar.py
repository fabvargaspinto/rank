import pytest

from core.user.domain.user_avatar import UserAvatar
from core.user.domain.user_error import InvalidUserAvatarError

PATH = "550e8400-e29b-41d4-a716-446655440000/avatar.webp"
NEW_PATH = (
    "550e8400-e29b-41d4-a716-446655440000/"
    "660e8400-e29b-41d4-a716-446655440000.webp"
)


class TestUserAvatar:

    def test_should_create_valid_avatar(self):
        avatar = UserAvatar(PATH)

        assert avatar.value == PATH

    def test_accepts_a_unique_webp_name(self):
        assert UserAvatar(NEW_PATH).value == NEW_PATH

    def test_should_reject_foreign_url(self):
        with pytest.raises(InvalidUserAvatarError):
            UserAvatar("https://otro-dominio.example/pixel.gif")

    def test_should_reject_url_without_https(self):
        with pytest.raises(InvalidUserAvatarError):
            UserAvatar("example.com/avatar.jpg")

    def test_should_reject_empty_url(self):
        with pytest.raises(InvalidUserAvatarError):
            UserAvatar("")

    def test_should_strip_external_spaces(self):
        avatar = UserAvatar(f" {PATH} ")

        assert avatar.value == PATH
