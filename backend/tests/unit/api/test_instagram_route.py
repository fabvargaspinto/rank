from datetime import UTC, datetime

from fastapi import FastAPI
from fastapi.testclient import TestClient

from api.dependencies.auth import (
    AuthJwtSettings,
    CurrentUser,
    get_auth_jwt_settings,
    get_current_user,
    get_jwks_client,
)
from api.dependencies.container import (
    get_capture_instagram_followers_use_case,
    get_complete_instagram_oauth_use_case,
    get_delete_instagram_user_data_use_case,
    get_disconnect_instagram_use_case,
    get_follower_history_use_case,
    get_instagram_connection_use_case,
    get_start_instagram_connection_use_case,
    get_user_use_case,
)
from api.errors import register_error_handlers
from api.rate_limit import register_rate_limit
from api.routers.instagram import get_instagram_settings
from api.routers.instagram import router as instagram_router
from config.instagram_settings import InstagramSettings
from core.instagram.application.capture_instagram_followers import (
    CaptureInstagramFollowers,
)
from core.instagram.application.complete_instagram_oauth import CompleteInstagramOAuth
from core.instagram.application.delete_instagram_user_data import (
    DeleteInstagramUserData,
)
from core.instagram.application.disconnect_instagram import DisconnectInstagram
from core.instagram.application.get_follower_history import GetFollowerHistory
from core.instagram.application.get_instagram_connection import GetInstagramConnection
from core.instagram.application.start_instagram_connection import (
    StartInstagramConnection,
)
from core.user.application.get_user import GetUser
from core.user.domain.user import User
from tests.unit.instagram.application.fake_repos import (
    FakeConnectionRepo,
    FakeSnapshotRepo,
)
from tests.unit.instagram.application.fakes import (
    AUTH_URL,
    FakeInstagramGraph,
    FakeOAuthStateCodec,
    FakeTokenCipher,
)
from tests.unit.user.application.fake_user_repo import FakeUserRepo

AUTH_ID = "660e8400-e29b-41d4-a716-446655440000"
NOW = datetime(2026, 10, 7, 12, 0, tzinfo=UTC)
ISSUER = "https://example.supabase.co/auth/v1"


class _UnusedJwksClient:
    def get_signing_key_from_jwt(self, token: str):
        raise AssertionError("JWKS should not be used without a Bearer token")


def _settings() -> InstagramSettings:
    return InstagramSettings(
        instagram_app_id="123",
        instagram_app_secret="secret",
        instagram_redirect_uri="http://localhost:3000/auth/instagram/callback",
        instagram_token_encryption_key="00" * 32,
        instagram_snapshot_job_token="job-secret",
    )


class _Harness:
    def __init__(self) -> None:
        self.user = User.create_empty()
        self.users = FakeUserRepo()
        self.users.users_by_auth_id[AUTH_ID] = self.user
        self.graph = FakeInstagramGraph()
        self.connections = FakeConnectionRepo()
        self.snapshots = FakeSnapshotRepo()
        self.cipher = FakeTokenCipher()
        self.codec = FakeOAuthStateCodec()
        self.clock = lambda: NOW
        self.capture = CaptureInstagramFollowers(
            self.graph,
            self.connections,
            self.snapshots,
            self.cipher,
            clock=self.clock,
        )
        self.client = self._client()

    def _client(self) -> TestClient:
        app = FastAPI()
        register_error_handlers(app)
        register_rate_limit(app)
        app.include_router(instagram_router)
        app.dependency_overrides[get_auth_jwt_settings] = lambda: AuthJwtSettings(
            jwks_url=f"{ISSUER}/.well-known/jwks.json",
            issuer=ISSUER,
        )
        app.dependency_overrides[get_jwks_client] = lambda: _UnusedJwksClient()
        app.dependency_overrides[get_user_use_case] = lambda: GetUser(self.users)
        app.dependency_overrides[get_current_user] = lambda: CurrentUser(
            auth_id=AUTH_ID,
            email="luna@example.com",
        )
        app.dependency_overrides[get_instagram_settings] = _settings
        app.dependency_overrides[get_start_instagram_connection_use_case] = (
            lambda: StartInstagramConnection(
                self.graph,
                self.codec,
                nonce_factory=lambda: "nonce-1",
                clock=self.clock,
            )
        )
        app.dependency_overrides[get_complete_instagram_oauth_use_case] = (
            lambda: CompleteInstagramOAuth(
                self.graph,
                self.connections,
                self.cipher,
                self.codec,
                self.capture,
                clock=self.clock,
            )
        )
        app.dependency_overrides[get_instagram_connection_use_case] = (
            lambda: GetInstagramConnection(self.connections, self.snapshots)
        )
        app.dependency_overrides[get_follower_history_use_case] = (
            lambda: GetFollowerHistory(self.connections, self.snapshots)
        )
        app.dependency_overrides[get_disconnect_instagram_use_case] = (
            lambda: DisconnectInstagram(self.connections, self.snapshots)
        )
        app.dependency_overrides[get_delete_instagram_user_data_use_case] = (
            lambda: DeleteInstagramUserData(self.connections, self.snapshots)
        )
        app.dependency_overrides[get_capture_instagram_followers_use_case] = (
            lambda: self.capture
        )
        return TestClient(app, follow_redirects=False)


def test_connect_requires_auth():
    app = FastAPI()
    register_error_handlers(app)
    register_rate_limit(app)
    app.include_router(instagram_router)
    app.dependency_overrides[get_auth_jwt_settings] = lambda: AuthJwtSettings(
        jwks_url=f"{ISSUER}/.well-known/jwks.json",
        issuer=ISSUER,
    )
    app.dependency_overrides[get_jwks_client] = lambda: _UnusedJwksClient()
    response = TestClient(app).get("/me/instagram/connect")

    assert response.status_code == 401


def test_connect_returns_authorization_url_without_secret():
    harness = _Harness()

    response = harness.client.get("/me/instagram/connect")

    assert response.status_code == 200
    url = response.json()["authorization_url"]
    assert url.startswith(AUTH_URL)
    assert "secret" not in url
    assert "access_token" not in response.text


def test_oauth_connects_and_hides_token_from_connection_payload():
    harness = _Harness()
    connect = harness.client.get("/me/instagram/connect")
    state = connect.json()["authorization_url"].removeprefix(AUTH_URL)

    oauth = harness.client.post(
        "/me/instagram/oauth",
        json={"code": "auth-code", "state": state},
    )
    connection = harness.client.get("/me/instagram")
    history = harness.client.get("/me/instagram/followers")

    assert oauth.status_code == 200
    body = oauth.json()
    assert body["connected"] is True
    assert body["username"] == "luna.reyes"
    assert body["avatar_url"] == (
        "https://scontent.cdninstagram.com/v/t51.2885-19/avatar.jpg"
    )
    assert body["followers_count"] == 1250
    assert "token" not in body
    assert "ig-access-token" not in connection.text
    assert history.json()["items"][0]["followers_count"] == 1250
    assert history.json()["items"][0]["week_start"] == "2026-10-05"


def test_oauth_error_returns_400():
    harness = _Harness()

    response = harness.client.post(
        "/me/instagram/oauth",
        json={"error": "access_denied", "state": "x"},
    )

    assert response.status_code == 400


def test_oauth_rejects_state_for_another_owner():
    harness = _Harness()
    connect = harness.client.get("/me/instagram/connect")
    state = connect.json()["authorization_url"].removeprefix(AUTH_URL)
    stranger = User.create_empty()
    harness.users.users_by_auth_id["770e8400-e29b-41d4-a716-446655440000"] = stranger
    harness.client.app.dependency_overrides[get_current_user] = lambda: CurrentUser(
        auth_id="770e8400-e29b-41d4-a716-446655440000",
        email="other@example.com",
    )

    response = harness.client.post(
        "/me/instagram/oauth",
        json={"code": "auth-code", "state": state},
    )

    assert response.status_code == 400
    assert harness.connections.get_by_owner(harness.user.id.value) is None
    assert harness.connections.get_by_owner(stranger.id.value) is None


def test_user_cannot_read_another_users_connection():
    harness = _Harness()
    connect = harness.client.get("/me/instagram/connect")
    state = connect.json()["authorization_url"].removeprefix(AUTH_URL)
    harness.client.post(
        "/me/instagram/oauth",
        json={"code": "auth-code", "state": state},
    )
    stranger = User.create_empty()
    harness.users.users_by_auth_id["770e8400-e29b-41d4-a716-446655440000"] = stranger
    harness.client.app.dependency_overrides[get_current_user] = lambda: CurrentUser(
        auth_id="770e8400-e29b-41d4-a716-446655440000",
        email="other@example.com",
    )

    response = harness.client.get("/me/instagram")

    assert response.json()["connected"] is False


def test_disconnect_and_job():
    harness = _Harness()
    connect = harness.client.get("/me/instagram/connect")
    state = connect.json()["authorization_url"].removeprefix(AUTH_URL)
    harness.client.post(
        "/me/instagram/oauth",
        json={"code": "auth-code", "state": state},
    )

    denied = harness.client.post("/internal/instagram/snapshots")
    allowed = harness.client.post(
        "/internal/instagram/snapshots",
        headers={"X-Job-Token": "job-secret"},
    )
    deleted = harness.client.delete("/me/instagram")
    missing = harness.client.get("/me/instagram/followers")

    assert denied.status_code == 401
    assert allowed.status_code == 200
    assert allowed.json() == {"captured": 1, "failed": 0, "needs_reconnect": 0}
    assert deleted.status_code == 204
    assert missing.status_code == 404


def _signed_request(user_id: str, secret: str = "secret") -> str:
    import hmac
    import json
    from base64 import urlsafe_b64encode
    from hashlib import sha256

    body = (
        urlsafe_b64encode(json.dumps({"user_id": user_id}).encode("utf-8"))
        .decode("ascii")
        .rstrip("=")
    )
    signature = (
        urlsafe_b64encode(
            hmac.new(secret.encode("utf-8"), body.encode("utf-8"), sha256).digest()
        )
        .decode("ascii")
        .rstrip("=")
    )
    return f"{signature}.{body}"


def test_meta_deauthorize_deletes_connection_and_snapshots():
    from datetime import timedelta

    from core.instagram.domain.follower_snapshot import FollowerSnapshot
    from core.instagram.domain.instagram_connection import InstagramConnection
    from core.instagram.domain.instagram_connection_repo import (
        StoredInstagramConnection,
    )

    harness = _Harness()
    account_id = "17841400000000000"
    connection = InstagramConnection.connect(
        harness.user.id.value,
        account_id,
        "luna.reyes",
        NOW + timedelta(days=40),
    )
    harness.connections.save(StoredInstagramConnection(connection, "enc:token"))
    harness.snapshots.save(FollowerSnapshot.capture(account_id, 1000, NOW))

    response = harness.client.post(
        "/instagram/deauthorize",
        data={"signed_request": _signed_request(account_id)},
    )

    assert response.status_code == 200
    assert response.json() == {"success": True}
    assert harness.connections.get_by_account(account_id) is None
    assert harness.snapshots.snapshots == []


def test_meta_data_deletion_returns_confirmation():
    harness = _Harness()

    response = harness.client.post(
        "/instagram/data-deletion",
        data={"signed_request": _signed_request("17841499999999999")},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["confirmation_code"]
    assert body["url"].startswith(
        "http://localhost:3000/instagram/data-deletion/status?code="
    )
