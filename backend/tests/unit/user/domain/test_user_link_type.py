import pytest

from core.user.domain.user_error import InvalidUserLinkTypeError
from core.user.domain.user_link_type import UserLinkType


class TestUserLinkType:

    def test_should_have_youtube_type(self):
        assert UserLinkType.YOUTUBE.value == "youtube"

    def test_should_have_instagram_type(self):
        assert UserLinkType.INSTAGRAM.value == "instagram"

    def test_should_have_default_type(self):
        assert UserLinkType.DEFAULT.value == "default"

    def test_default_should_be_default_type(self):
        assert UserLinkType.DEFAULT.is_default() is True

    def test_youtube_should_not_be_default_type(self):
        assert UserLinkType.YOUTUBE.is_default() is False

    def test_instagram_should_not_be_default_type(self):
        assert UserLinkType.INSTAGRAM.is_default() is False

    def test_youtube_should_have_youtube_hosts(self):
        assert UserLinkType.YOUTUBE.hosts() == (
            "youtube.com",
            "www.youtube.com",
            "m.youtube.com",
            "youtu.be",
            "music.youtube.com",
        )

    def test_instagram_should_have_instagram_hosts(self):
        assert UserLinkType.INSTAGRAM.hosts() == (
            "instagram.com",
            "www.instagram.com",
        )

    def test_default_should_have_no_hosts(self):
        assert UserLinkType.DEFAULT.hosts() == ()

    def test_should_create_type_from_string(self):
        link_type = UserLinkType.from_string("youtube")

        assert link_type == UserLinkType.YOUTUBE

    def test_should_create_type_from_uppercase_string(self):
        link_type = UserLinkType.from_string("INSTAGRAM")

        assert link_type == UserLinkType.INSTAGRAM

    def test_should_remove_spaces_from_type(self):
        link_type = UserLinkType.from_string(" DEFAULT ")

        assert link_type == UserLinkType.DEFAULT

    def test_should_reject_unknown_type(self):
        with pytest.raises(InvalidUserLinkTypeError):
            UserLinkType.from_string("tiktok")

    def test_should_get_all_types(self):
        assert UserLinkType.get_all() == ["youtube", "instagram", "default"]
