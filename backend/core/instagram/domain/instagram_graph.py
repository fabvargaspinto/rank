from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from core.instagram.domain.errors import InvalidInstagramTokenError
from core.instagram.domain.instagram_account import InstagramAccount


@dataclass(frozen=True)
class InstagramAccessToken:
    value: str
    expires_at: datetime

    def __post_init__(self) -> None:
        if not isinstance(self.value, str) or not self.value.strip():
            raise InvalidInstagramTokenError("El token de Instagram no es válido")
        if self.expires_at.tzinfo is None or self.expires_at.utcoffset() is None:
            raise InvalidInstagramTokenError("El token de Instagram no es válido")
        object.__setattr__(self, "value", self.value.strip())

    def __repr__(self) -> str:
        return "InstagramAccessToken(redacted)"

    def __str__(self) -> str:
        return "InstagramAccessToken(redacted)"


@dataclass(frozen=True)
class CompletedInstagramLogin:
    token: InstagramAccessToken
    account: InstagramAccount
    followers_count: int


@dataclass(frozen=True)
class InstagramProfile:
    account: InstagramAccount
    followers_count: int


class InstagramGraph(Protocol):
    def authorization_url(self, state: str) -> str:
        pass

    def complete_login(self, code: str) -> CompletedInstagramLogin:
        pass

    def fetch_profile(self, access_token: str) -> InstagramProfile:
        pass

    def refresh_access_token(self, access_token: str) -> InstagramAccessToken:
        pass
