from datetime import UTC, datetime

from core.instagram.application.application_error import InstagramGraphError
from core.instagram.domain.instagram_account import InstagramAccount
from core.instagram.domain.instagram_graph import (
    CompletedInstagramLogin,
    InstagramAccessToken,
    InstagramGraph,
)

ACCOUNT_ID = "17841400000000000"
USERNAME = "luna.reyes"
ACCESS_TOKEN = "ig-access-token"
AUTH_URL = "https://www.instagram.com/oauth/authorize?state="


class FakeInstagramGraph(InstagramGraph):
    def __init__(self) -> None:
        self.account_id = ACCOUNT_ID
        self.username = USERNAME
        self.avatar_url = "https://scontent.cdninstagram.com/v/t51.2885-19/avatar.jpg"
        self.access_token = ACCESS_TOKEN
        self.followers = 1250
        self.expires_at = datetime(2026, 12, 1, tzinfo=UTC)
        self.fail_login = False
        self.fail_followers = False
        self.fail_refresh = False
        self.refreshed_token = "ig-refreshed-token"
        self.refreshed_expires_at = datetime(2027, 1, 1, tzinfo=UTC)
        self.complete_login_calls: list[str] = []
        self.fetch_followers_tokens: list[str] = []
        self.refresh_tokens: list[str] = []

    def authorization_url(self, state: str) -> str:
        return f"{AUTH_URL}{state}"

    def complete_login(self, code: str) -> CompletedInstagramLogin:
        self.complete_login_calls.append(code)
        if self.fail_login:
            raise InstagramGraphError("Instagram no está disponible")
        return CompletedInstagramLogin(
            token=InstagramAccessToken(self.access_token, self.expires_at),
            account=InstagramAccount.create(
                self.account_id,
                self.username,
                self.avatar_url,
            ),
            followers_count=self.followers,
        )

    def fetch_followers(self, access_token: str) -> int:
        self.fetch_followers_tokens.append(access_token)
        if self.fail_followers:
            raise InstagramGraphError("Instagram no está disponible")
        return self.followers

    def refresh_access_token(self, access_token: str) -> InstagramAccessToken:
        self.refresh_tokens.append(access_token)
        if self.fail_refresh:
            raise InstagramGraphError("Instagram no está disponible")
        return InstagramAccessToken(self.refreshed_token, self.refreshed_expires_at)


class FakeTokenCipher:
    def encrypt(self, token: str, *, associated_data: str) -> str:
        return f"enc:{associated_data}:{token}"

    def decrypt(self, encrypted: str, *, associated_data: str) -> str:
        prefix = f"enc:{associated_data}:"
        if encrypted.startswith(prefix):
            return encrypted[len(prefix) :]
        if encrypted.startswith("enc:"):
            return encrypted[len("enc:") :]
        return encrypted


class FakeOAuthStateCodec:
    def __init__(self) -> None:
        self._states: dict[str, object] = {}
        self.invalid = False

    def dumps(self, state: object) -> str:
        key = f"state-{len(self._states) + 1}"
        self._states[key] = state
        return key

    def loads(self, value: str) -> object:
        from core.instagram.application.application_error import (
            InstagramOAuthStateError,
        )

        if self.invalid:
            raise InstagramOAuthStateError("El inicio de sesión de Instagram no es válido")
        state = self._states.get(value)
        if state is None:
            raise InstagramOAuthStateError("El inicio de sesión de Instagram no es válido")
        return state
