from datetime import UTC, datetime, timedelta

import pytest

from core.instagram.application.application_error import (
    InstagramAccountAlreadyLinkedError,
    InstagramNotConnectedError,
    InstagramOAuthDeniedError,
    InstagramOAuthStateError,
)
from core.instagram.application.capture_instagram_followers import (
    CaptureInstagramFollowers,
)
from core.instagram.application.complete_instagram_oauth import CompleteInstagramOAuth
from core.instagram.application.disconnect_instagram import DisconnectInstagram
from core.instagram.application.get_follower_history import GetFollowerHistory
from core.instagram.application.get_instagram_connection import GetInstagramConnection
from core.instagram.application.start_instagram_connection import (
    StartInstagramConnection,
)
from core.instagram.domain.instagram_connection import InstagramConnection
from core.instagram.domain.instagram_connection_repo import StoredInstagramConnection
from core.shared.domain.domain_error import InvalidUUIDError
from tests.unit.instagram.application.fake_repos import (
    FakeConnectionRepo,
    FakeSnapshotRepo,
)
from tests.unit.instagram.application.fakes import (
    ACCESS_TOKEN,
    ACCOUNT_ID,
    AUTH_URL,
    FakeInstagramGraph,
    FakeOAuthStateCodec,
    FakeTokenCipher,
)

OWNER_ID = "550e8400-e29b-41d4-a716-446655440000"
OTHER_OWNER_ID = "660e8400-e29b-41d4-a716-446655440000"
NOW = datetime(2026, 10, 7, 12, 0, tzinfo=UTC)


class TestStartInstagramConnection:
    def setup_method(self):
        self.graph = FakeInstagramGraph()
        self.codec = FakeOAuthStateCodec()
        self.use_case = StartInstagramConnection(
            self.graph,
            self.codec,
            nonce_factory=lambda: "nonce-1",
            clock=lambda: NOW,
        )

    def test_returns_authorization_url_with_signed_state(self):
        url = self.use_case.execute(OWNER_ID)

        assert url.startswith(AUTH_URL)
        state = url.removeprefix(AUTH_URL)
        payload = self.codec.loads(state)
        assert payload.owner_user_id.value == OWNER_ID
        assert payload.nonce == "nonce-1"

    def test_rejects_owner_that_is_not_a_uuid(self):
        with pytest.raises(InvalidUUIDError):
            self.use_case.execute("not-a-uuid")


class TestCompleteInstagramOAuth:
    def setup_method(self):
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
        self.use_case = CompleteInstagramOAuth(
            self.graph,
            self.connections,
            self.cipher,
            self.codec,
            self.capture,
            clock=self.clock,
        )
        self.start = StartInstagramConnection(
            self.graph,
            self.codec,
            nonce_factory=lambda: "nonce-1",
            clock=self.clock,
        )

    def _state(self) -> str:
        url = self.start.execute(OWNER_ID)
        return url.removeprefix(AUTH_URL)

    def test_connects_account_and_captures_first_snapshot(self):
        connection = self.use_case.execute(self._state(), "auth-code")

        stored = self.connections.get_by_owner(OWNER_ID)
        assert stored is not None
        assert stored.connection.id == connection.id
        assert stored.connection.account.id.value == ACCOUNT_ID
        assert stored.access_token_encrypted == f"enc:{ACCESS_TOKEN}"
        assert self.graph.complete_login_calls == ["auth-code"]
        assert len(self.snapshots.snapshots) == 1
        assert self.snapshots.snapshots[0].followers_count.value == 1250

    def test_denies_when_user_rejects_permissions(self):
        with pytest.raises(InstagramOAuthDeniedError):
            self.use_case.execute(self._state(), None, error="access_denied")

        assert self.connections.list_all() == []

    def test_rejects_invalid_state(self):
        self.codec.invalid = True

        with pytest.raises(InstagramOAuthStateError):
            self.use_case.execute("tampered", "auth-code")

    def test_rejects_account_linked_to_another_owner(self):
        other = InstagramConnection.connect(
            OTHER_OWNER_ID,
            ACCOUNT_ID,
            "otra",
            NOW + timedelta(days=30),
        )
        self.connections.save(
            StoredInstagramConnection(other, "enc:other-token")
        )

        with pytest.raises(InstagramAccountAlreadyLinkedError):
            self.use_case.execute(self._state(), "auth-code")

    def test_reauthorize_replaces_token_for_same_owner(self):
        first = self.use_case.execute(self._state(), "auth-code")
        self.graph.access_token = "ig-new-token"
        self.graph.username = "luna.nueva"

        updated = self.use_case.execute(self._state(), "auth-code-2")

        assert updated.id == first.id
        stored = self.connections.get_by_owner(OWNER_ID)
        assert stored is not None
        assert stored.access_token_encrypted == "enc:ig-new-token"
        assert stored.connection.account.username.value == "luna.nueva"


class TestDisconnectAndQueries:
    def setup_method(self):
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
        self.complete = CompleteInstagramOAuth(
            self.graph,
            self.connections,
            self.cipher,
            self.codec,
            self.capture,
            clock=self.clock,
        )
        self.start = StartInstagramConnection(
            self.graph,
            self.codec,
            nonce_factory=lambda: "nonce-1",
            clock=self.clock,
        )

    def _connect(self) -> None:
        url = self.start.execute(OWNER_ID)
        self.complete.execute(url.removeprefix(AUTH_URL), "auth-code")

    def test_get_connection_when_disconnected(self):
        view = GetInstagramConnection(self.connections, self.snapshots).execute(
            OWNER_ID
        )

        assert view.connected is False
        assert view.followers_count is None

    def test_get_connection_and_history_after_connect(self):
        self._connect()

        view = GetInstagramConnection(self.connections, self.snapshots).execute(
            OWNER_ID
        )
        history = GetFollowerHistory(self.connections, self.snapshots).execute(
            OWNER_ID
        )

        assert view.connected is True
        assert view.username == "luna.reyes"
        assert view.followers_count == 1250
        assert view.followers_delta is None
        assert len(history) == 1
        assert history[0].followers_count == 1250
        assert history[0].delta is None
        assert history[0].week_start.isoformat() == "2026-10-05"

    def test_history_requires_connection(self):
        with pytest.raises(InstagramNotConnectedError):
            GetFollowerHistory(self.connections, self.snapshots).execute(OWNER_ID)

    def test_disconnect_removes_connection_and_snapshots(self):
        self._connect()

        DisconnectInstagram(self.connections, self.snapshots).execute(OWNER_ID)

        assert self.connections.get_by_owner(OWNER_ID) is None
        assert self.snapshots.snapshots == []

    def test_disconnect_when_missing_raises(self):
        with pytest.raises(InstagramNotConnectedError):
            DisconnectInstagram(self.connections, self.snapshots).execute(OWNER_ID)

    def test_queries_do_not_expose_access_token(self):
        self._connect()

        view = GetInstagramConnection(self.connections, self.snapshots).execute(
            OWNER_ID
        )

        assert ACCESS_TOKEN not in repr(view)
        assert "enc:" not in repr(view)
