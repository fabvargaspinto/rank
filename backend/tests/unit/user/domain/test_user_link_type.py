import pytest

from core.user.domain.user_error import InvalidUserLinkTypeError
from core.user.domain.user_link_type import UserLinkType


class TestUserLinkType:

    def test_should_have_youtube_type(self):
        assert UserLinkType.YOUTUBE.value == "youtube"

    def test_should_have_instagram_type(self):
        assert UserLinkType.INSTAGRAM.value == "instagram"

    def test_should_have_spotify_type(self):
        assert UserLinkType.SPOTIFY.value == "spotify"

    def test_should_have_tiktok_type(self):
        assert UserLinkType.TIKTOK.value == "tiktok"

    def test_should_have_twitch_type(self):
        assert UserLinkType.TWITCH.value == "twitch"

    def test_should_have_kick_type(self):
        assert UserLinkType.KICK.value == "kick"

    def test_should_have_facebook_type(self):
        assert UserLinkType.FACEBOOK.value == "facebook"

    def test_should_have_default_type(self):
        assert UserLinkType.DEFAULT.value == "default"

    def test_should_have_x_type(self):
        assert UserLinkType.X.value == "x"


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

    def test_spotify_should_have_spotify_hosts(self):
        assert UserLinkType.SPOTIFY.hosts() == (
            "spotify.com",
            "www.spotify.com",
        )

    def test_tiktok_should_have_tiktok_hosts(self):
        assert UserLinkType.TIKTOK.hosts() == (
            "tiktok.com",
            "www.tiktok.com",
        )

    def test_twitch_should_have_twitch_hosts(self):
        assert UserLinkType.TWITCH.hosts() == (
            "twitch.tv",
            "www.twitch.tv",
        )

    def test_kick_should_have_kick_hosts(self):
        assert UserLinkType.KICK.hosts() == (
            "kick.com",
            "www.kick.com",
        )

    def test_facebook_should_have_facebook_hosts(self):
        assert UserLinkType.FACEBOOK.hosts() == (
            "facebook.com",
            "www.facebook.com",
        )

    def test_x_should_have_x_hosts(self):
        assert UserLinkType.X.hosts() == (
            "x.com",
            "www.x.com",
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
            UserLinkType.from_string("linkedin")

    def test_should_get_all_types(self):
        assert UserLinkType.get_all() == [
            "youtube",
            "instagram",
            "spotify",
            "tiktok",
            "twitch",
            "kick",
            "facebook",
            "x",
            "default",
        ]

    def test_from_host_matches_known_network(self):
        assert UserLinkType.from_host("www.youtube.com") == UserLinkType.YOUTUBE
        assert UserLinkType.from_host("instagram.com") == UserLinkType.INSTAGRAM

    def test_from_host_falls_back_to_default(self):
        assert UserLinkType.from_host("example.com") == UserLinkType.DEFAULT
