from enum import StrEnum

from core.user.domain.user_error import InvalidUserLinkTypeError


class UserLinkType(StrEnum):
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    SPOTIFY = "spotify"
    TIKTOK = "tiktok"
    TWITCH = "twitch"
    KICK = "kick"
    FACEBOOK = "facebook"
    X = "x"
    SOUNDCLOUD = "soundcloud"
    BANDCAMP = "bandcamp"
    APPLE_MUSIC = "apple_music"
    DEFAULT = "default"

    def hosts(self) -> tuple[str, ...]:
        if self is UserLinkType.YOUTUBE:
            return (
                "youtube.com",
                "www.youtube.com",
                "m.youtube.com",
                "youtu.be",
                "music.youtube.com",
            )
        if self is UserLinkType.INSTAGRAM:
            return ("instagram.com", "www.instagram.com")
        if self is UserLinkType.SPOTIFY:
            return ("spotify.com", "www.spotify.com", "open.spotify.com")
        if self is UserLinkType.TIKTOK:
            return ("tiktok.com", "www.tiktok.com")
        if self is UserLinkType.TWITCH:
            return ("twitch.tv", "www.twitch.tv")
        if self is UserLinkType.KICK:
            return ("kick.com", "www.kick.com")
        if self is UserLinkType.FACEBOOK:
            return ("facebook.com", "www.facebook.com", "fb.com", "www.fb.com")
        if self is UserLinkType.X:
            return ("x.com", "www.x.com", "twitter.com", "www.twitter.com")
        if self is UserLinkType.SOUNDCLOUD:
            return (
                "soundcloud.com",
                "www.soundcloud.com",
                "m.soundcloud.com",
                "on.soundcloud.com",
            )
        if self is UserLinkType.BANDCAMP:
            return ("bandcamp.com", "www.bandcamp.com")
        if self is UserLinkType.APPLE_MUSIC:
            return ("music.apple.com", "www.music.apple.com")
        return ()

    def matches(self, host: str) -> bool:
        if host in self.hosts():
            return True
        return self is UserLinkType.BANDCAMP and host.endswith(".bandcamp.com")

    def is_default(self) -> bool:
        return self is UserLinkType.DEFAULT

    @classmethod
    def from_host(cls, host: str) -> "UserLinkType":
        normalized = host.strip().lower()
        for link_type in cls:
            if link_type.is_default():
                continue
            if link_type.matches(normalized):
                return link_type
        return cls.DEFAULT

    @classmethod
    def from_string(cls, value: str) -> "UserLinkType":
        normalized = value.strip().lower()
        try:
            return cls(normalized)
        except ValueError as exc:
            allowed = ", ".join(link_type.value for link_type in cls)
            raise InvalidUserLinkTypeError(
                f"El tipo de link debe ser uno de los siguientes: {allowed}"
            ) from exc
