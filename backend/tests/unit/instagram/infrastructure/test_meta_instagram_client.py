from urllib.parse import parse_qs, urlparse

import httpx

from config.instagram_settings import InstagramSettings
from core.instagram.infrastructure.meta_instagram_client import MetaInstagramClient

TOKEN = "IGQWB-long-lived"
SHORT_TOKEN = "IGQWB-short"


def _settings() -> InstagramSettings:
    return InstagramSettings(
        instagram_app_id="104977",
        instagram_app_secret="app-secret",
        instagram_redirect_uri="http://localhost:3000/auth/instagram/callback",
        instagram_token_encryption_key="00" * 32,
    )


def _handler(request: httpx.Request) -> httpx.Response:
    url = str(request.url)
    if request.method == "POST" and request.url.path.endswith("/oauth/access_token"):
        return httpx.Response(
            200,
            json={"access_token": SHORT_TOKEN, "user_id": "17841400000000000"},
        )
    if "grant_type=ig_exchange_token" in url:
        return httpx.Response(
            200,
            json={"access_token": TOKEN, "token_type": "bearer", "expires_in": 5184000},
        )
    if request.url.path.endswith("/me"):
        return httpx.Response(
            200,
            json={
                "user_id": "17841400000000000",
                "username": "luna.reyes",
                "followers_count": 1390,
                "profile_picture_url": "https://scontent.cdninstagram.com/v/t51.2885-19/avatar.jpg",
            },
        )
    if "refresh_access_token" in url:
        return httpx.Response(
            200,
            json={
                "access_token": "IGQWB-refreshed",
                "token_type": "bearer",
                "expires_in": 5184000,
            },
        )
    return httpx.Response(404, json={"error": {"message": "missing"}})


def _client() -> MetaInstagramClient:
    return MetaInstagramClient(
        _settings(),
        http=httpx.Client(transport=httpx.MockTransport(_handler)),
    )


def test_authorization_url_does_not_include_app_secret():
    url = _client().authorization_url("signed-state")
    parsed = urlparse(url)
    query = parse_qs(parsed.query)

    assert parsed.netloc == "www.instagram.com"
    assert query["client_id"] == ["104977"]
    assert query["state"] == ["signed-state"]
    assert query["enable_fb_login"] == ["false"]
    assert "app-secret" not in url
    assert "client_secret" not in query


def test_complete_login_maps_meta_payload_to_domain():
    login = _client().complete_login("AUTHCODE#_")

    assert login.account.id.value == "17841400000000000"
    assert login.account.username.value == "luna.reyes"
    assert login.account.avatar_url is not None
    assert login.account.avatar_url.value.endswith("/avatar.jpg")
    assert login.followers_count == 1390
    assert login.token.value == TOKEN
    assert TOKEN not in repr(login.token)


def test_fetch_profile_and_refresh():
    client = _client()

    profile = client.fetch_profile(TOKEN)
    assert profile.followers_count == 1390
    assert profile.account.username.value == "luna.reyes"
    assert profile.account.avatar_url is not None
    assert profile.account.avatar_url.value.endswith("/avatar.jpg")
    refreshed = client.refresh_access_token(TOKEN)
    assert refreshed.value == "IGQWB-refreshed"


def test_complete_login_fails_when_long_lived_exchange_fails():
    from core.instagram.application.application_error import InstagramGraphError

    def handler(request: httpx.Request) -> httpx.Response:
        url = str(request.url)
        if request.method == "POST" and request.url.path.endswith("/oauth/access_token"):
            return httpx.Response(
                200,
                json={"access_token": SHORT_TOKEN, "user_id": "17841400000000000"},
            )
        if "grant_type=ig_exchange_token" in url:
            return httpx.Response(
                400,
                json={"error": {"message": "Invalid token", "type": "OAuthException"}},
            )
        return httpx.Response(404, json={"error": {"message": "missing"}})

    client = MetaInstagramClient(
        _settings(),
        http=httpx.Client(transport=httpx.MockTransport(handler)),
    )

    try:
        client.complete_login("AUTHCODE")
        raise AssertionError("expected InstagramGraphError")
    except InstagramGraphError:
        pass


def test_fetch_profile_raises_token_expired_on_oauth_code_190():
    from core.instagram.application.application_error import InstagramTokenExpiredError

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            400,
            json={
                "error": {
                    "message": "Invalid OAuth access token",
                    "type": "OAuthException",
                    "code": 190,
                    "error_subcode": 467,
                }
            },
        )

    client = MetaInstagramClient(
        _settings(),
        http=httpx.Client(transport=httpx.MockTransport(handler)),
    )

    try:
        client.fetch_profile(TOKEN)
        raise AssertionError("expected InstagramTokenExpiredError")
    except InstagramTokenExpiredError:
        pass
