import pytest

from core.shared.domain.user_id import UserId
from core.user.domain.user_avatar import UserAvatar
from core.user.domain.user_error import InvalidUserAvatarError

USER_ID = "550e8400-e29b-41d4-a716-446655440000"
FILE_ID = "660e8400-e29b-41d4-a716-446655440000"
PATH = f"{USER_ID}/{FILE_ID}.webp"
OTHER_USER_ID = "770e8400-e29b-41d4-a716-446655440000"


class TestUserAvatar:
    def test_should_create_valid_avatar(self):
        avatar = UserAvatar(PATH)

        assert avatar.value == PATH

    def test_belongs_to_owning_user(self):
        avatar = UserAvatar(PATH)

        assert avatar.belongs_to(UserId(USER_ID)) is True
        assert avatar.belongs_to(UserId(OTHER_USER_ID)) is False

    def test_should_reject_legacy_avatar_filename(self):
        with pytest.raises(InvalidUserAvatarError):
            UserAvatar(f"{USER_ID}/avatar.webp")

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
