from __future__ import annotations

from datetime import UTC, datetime, timedelta
from urllib.parse import urlencode

import httpx

from config.instagram_settings import InstagramSettings
from core.instagram.application.application_error import InstagramGraphError
from core.instagram.domain.instagram_account import InstagramAccount
from core.instagram.domain.instagram_graph import (
    CompletedInstagramLogin,
    InstagramAccessToken,
    InstagramGraph,
)

_AUTHORIZE_URL = "https://www.instagram.com/oauth/authorize"
_TOKEN_URL = "https://api.instagram.com/oauth/access_token"
_GRAPH_URL = "https://graph.instagram.com"
_SCOPES = "instagram_business_basic"
_SHORT_LIVED_SECONDS = 3600


class MetaInstagramClient(InstagramGraph):
    def __init__(
        self,
        settings: InstagramSettings,
        http: httpx.Client | None = None,
    ) -> None:
        self._settings = settings
        self._http = http or httpx.Client(timeout=15.0)
        self._owns_http = http is None

    def authorization_url(self, state: str) -> str:
        query = urlencode(
            {
                "client_id": self._settings.instagram_app_id,
                "redirect_uri": self._settings.instagram_redirect_uri,
                "response_type": "code",
                "scope": _SCOPES,
                "state": state,
                "force_reauth": "true",
                "enable_fb_login": "false",
            }
        )
        return f"{_AUTHORIZE_URL}?{query}"

    def complete_login(self, code: str) -> CompletedInstagramLogin:
        short_token = self._exchange_code(_strip_code(code))
        token = self._exchange_long_lived(short_token)
        account, followers = self._fetch_profile(token.value)
        return CompletedInstagramLogin(
            token=token,
            account=account,
            followers_count=followers,
        )

    def fetch_followers(self, access_token: str) -> int:
        _, followers = self._fetch_profile(access_token)
        return followers

    def refresh_access_token(self, access_token: str) -> InstagramAccessToken:
        payload = self._get_json(
            f"{_GRAPH_URL}/refresh_access_token",
            {
                "grant_type": "ig_refresh_token",
                "access_token": access_token,
            },
        )
        return self._token_from_payload(payload, default_seconds=_SHORT_LIVED_SECONDS)

    def close(self) -> None:
        if self._owns_http:
            self._http.close()

    def _exchange_code(self, code: str) -> str:
        payload = self._post_form(
            _TOKEN_URL,
            {
                "client_id": self._settings.instagram_app_id,
                "client_secret": self._settings.instagram_app_secret,
                "grant_type": "authorization_code",
                "redirect_uri": self._settings.instagram_redirect_uri,
                "code": code,
            },
        )
        token = _extract_access_token(payload)
        if token is None:
            raise InstagramGraphError("Instagram no está disponible")
        return token

    def _exchange_long_lived(self, short_token: str) -> InstagramAccessToken:
        try:
            payload = self._get_json(
                f"{_GRAPH_URL}/access_token",
                {
                    "grant_type": "ig_exchange_token",
                    "client_secret": self._settings.instagram_app_secret,
                    "access_token": short_token,
                },
            )
            return self._token_from_payload(payload, default_seconds=60 * 60 * 24 * 60)
        except InstagramGraphError:
            return InstagramAccessToken(
                short_token,
                datetime.now(UTC) + timedelta(seconds=_SHORT_LIVED_SECONDS),
            )

    def _fetch_profile(self, access_token: str) -> tuple[InstagramAccount, int]:
        payload = self._get_json(
            f"{_GRAPH_URL}/me",
            {
                "fields": "user_id,username,followers_count",
                "access_token": access_token,
            },
        )
        account_id = str(payload.get("user_id") or payload.get("id") or "").strip()
        username = str(payload.get("username") or "").strip()
        followers = _as_int(payload.get("followers_count"))
        if not account_id or not username or followers is None:
            raise InstagramGraphError("Instagram no está disponible")
        return InstagramAccount.create(account_id, username), followers

    def _token_from_payload(
        self,
        payload: dict[str, object],
        *,
        default_seconds: int,
    ) -> InstagramAccessToken:
        token = _extract_access_token(payload)
        if token is None:
            raise InstagramGraphError("Instagram no está disponible")
        expires_in = _as_int(payload.get("expires_in")) or default_seconds
        return InstagramAccessToken(
            token,
            datetime.now(UTC) + timedelta(seconds=expires_in),
        )

    def _post_form(self, url: str, data: dict[str, str]) -> dict[str, object]:
        try:
            response = self._http.post(url, data=data)
        except httpx.HTTPError as exc:
            raise InstagramGraphError("Instagram no está disponible") from exc
        return self._read_json(response)

    def _get_json(self, url: str, params: dict[str, str]) -> dict[str, object]:
        try:
            response = self._http.get(url, params=params)
        except httpx.HTTPError as exc:
            raise InstagramGraphError("Instagram no está disponible") from exc
        return self._read_json(response)

    def _read_json(self, response: httpx.Response) -> dict[str, object]:
        if response.status_code >= 400:
            raise InstagramGraphError("Instagram no está disponible")
        try:
            payload = response.json()
        except ValueError as exc:
            raise InstagramGraphError("Instagram no está disponible") from exc
        if not isinstance(payload, dict):
            raise InstagramGraphError("Instagram no está disponible")
        if payload.get("error"):
            raise InstagramGraphError("Instagram no está disponible")
        return payload


def _strip_code(code: str) -> str:
    return code.strip().split("#", 1)[0]


def _extract_access_token(payload: dict[str, object]) -> str | None:
    token = payload.get("access_token")
    if isinstance(token, str) and token.strip():
        return token.strip()
    data = payload.get("data")
    if isinstance(data, list) and data:
        first = data[0]
        if isinstance(first, dict):
            nested = first.get("access_token")
            if isinstance(nested, str) and nested.strip():
                return nested.strip()
    return None


def _as_int(value: object) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.strip().isdigit():
        return int(value.strip())
    return None
