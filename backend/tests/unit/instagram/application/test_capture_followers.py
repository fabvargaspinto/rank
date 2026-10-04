from datetime import UTC, datetime, timedelta

from core.instagram.application.capture_instagram_followers import (
    CaptureInstagramFollowers,
)
from core.instagram.application.complete_instagram_oauth import CompleteInstagramOAuth
from core.instagram.application.get_follower_history import GetFollowerHistory
from core.instagram.application.start_instagram_connection import (
    StartInstagramConnection,
)
from tests.unit.instagram.application.fake_repos import (
    FakeConnectionRepo,
    FakeSnapshotRepo,
)
from tests.unit.instagram.application.fakes import (
    ACCESS_TOKEN,
    AUTH_URL,
    FakeInstagramGraph,
    FakeOAuthStateCodec,
    FakeTokenCipher,
)

OWNER_ID = "550e8400-e29b-41d4-a716-446655440000"
NOW = datetime(2026, 10, 7, 12, 0, tzinfo=UTC)


def _wired(now: datetime):
    graph = FakeInstagramGraph()
    connections = FakeConnectionRepo()
    snapshots = FakeSnapshotRepo()
    cipher = FakeTokenCipher()
    codec = FakeOAuthStateCodec()
    capture = CaptureInstagramFollowers(
        graph,
        connections,
        snapshots,
        cipher,
        clock=lambda: now,
    )
    complete = CompleteInstagramOAuth(
        graph,
        connections,
        cipher,
        codec,
        capture,
        clock=lambda: now,
    )
    start = StartInstagramConnection(
        graph,
        codec,
        nonce_factory=lambda: "nonce-1",
        clock=lambda: now,
    )
    return graph, connections, snapshots, cipher, capture, complete, start


class TestCaptureInstagramFollowers:
    def test_second_run_in_the_same_week_is_idempotent(self):
        graph, connections, snapshots, _, capture, complete, start = _wired(NOW)
        complete.execute(OWNER_ID, start.execute(OWNER_ID).removeprefix(AUTH_URL), "code")
        graph.followers = 1260

        first = snapshots.snapshots[0]
        second = capture.execute_for_owner(OWNER_ID)

        assert second.id == first.id
        assert second.week_start == first.week_start
        assert second.followers_count.value == 1260
        assert len(snapshots.snapshots) == 1

    def test_next_week_creates_a_new_snapshot(self):
        graph, connections, snapshots, _, capture, complete, start = _wired(NOW)
        complete.execute(OWNER_ID, start.execute(OWNER_ID).removeprefix(AUTH_URL), "code")
        graph.followers = 1341
        later = CaptureInstagramFollowers(
            graph,
            connections,
            snapshots,
            FakeTokenCipher(),
            clock=lambda: NOW + timedelta(days=7),
        )

        later.execute_for_owner(OWNER_ID)
        history = GetFollowerHistory(connections, snapshots).execute(OWNER_ID)

        assert len(snapshots.snapshots) == 2
        assert history[0].followers_count == 1250
        assert history[1].followers_count == 1341
        assert history[1].delta == 91

    def test_execute_all_captures_every_connection(self):
        graph, connections, snapshots, cipher, capture, complete, start = _wired(NOW)
        complete.execute(OWNER_ID, start.execute(OWNER_ID).removeprefix(AUTH_URL), "code")
        other = StartInstagramConnection(
            graph,
            FakeOAuthStateCodec(),
            nonce_factory=lambda: "nonce-2",
            clock=lambda: NOW,
        )
        other_codec = other._state_codec
        graph.account_id = "17841411111111111"
        url = other.execute("770e8400-e29b-41d4-a716-446655440000")
        CompleteInstagramOAuth(
            graph,
            connections,
            cipher,
            other_codec,
            capture,
            clock=lambda: NOW,
        ).execute(
            "770e8400-e29b-41d4-a716-446655440000",
            url.removeprefix(AUTH_URL),
            "code-2",
        )

        graph.followers = 2000
        result = capture.execute_all()

        assert result.captured == 2
        assert result.failed == 0
        assert result.needs_reconnect == 0
        assert len(snapshots.snapshots) == 2

    def test_execute_all_continues_when_one_account_fails(self):
        graph, connections, snapshots, _, capture, complete, start = _wired(NOW)
        complete.execute(OWNER_ID, start.execute(OWNER_ID).removeprefix(AUTH_URL), "code")
        graph.fail_followers = True

        result = capture.execute_all()

        assert result.captured == 0
        assert result.failed == 1
        assert result.needs_reconnect == 0

    def test_execute_all_marks_revoked_token_as_needs_reconnect(self):
        graph, connections, snapshots, _, capture, complete, start = _wired(NOW)
        complete.execute(OWNER_ID, start.execute(OWNER_ID).removeprefix(AUTH_URL), "code")
        graph.fail_auth = True
        graph.fetch_profile_tokens.clear()

        result = capture.execute_all()

        assert result.captured == 0
        assert result.failed == 0
        assert result.needs_reconnect == 1
        stored = connections.get_by_owner(OWNER_ID)
        assert stored is not None
        assert stored.connection.token_is_expired(NOW)
        assert graph.fetch_profile_tokens == [ACCESS_TOKEN]

        again = capture.execute_all()
        assert again.needs_reconnect == 1
        assert again.failed == 0
        assert graph.fetch_profile_tokens == [ACCESS_TOKEN]

    def test_execute_all_continues_when_token_decrypt_fails(self):
        from core.instagram.infrastructure.error_infrastructure import TokenDecryptError

        graph, connections, snapshots, cipher, capture, complete, start = _wired(NOW)
        complete.execute(
            OWNER_ID,
            start.execute(OWNER_ID).removeprefix(AUTH_URL),
            "code",
        )
        other_owner = "770e8400-e29b-41d4-a716-446655440000"
        other_start = StartInstagramConnection(
            graph,
            FakeOAuthStateCodec(),
            nonce_factory=lambda: "nonce-2",
            clock=lambda: NOW,
        )
        graph.account_id = "17841411111111111"
        url = other_start.execute(other_owner)
        CompleteInstagramOAuth(
            graph,
            connections,
            cipher,
            other_start._state_codec,
            capture,
            clock=lambda: NOW,
        ).execute(other_owner, url.removeprefix(AUTH_URL), "code-2")

        broken = connections.get_by_owner(OWNER_ID)
        assert broken is not None
        fail_id = broken.connection.id.value

        class DecryptFailCipher(FakeTokenCipher):
            def decrypt(self, encrypted: str, *, associated_data: str) -> str:
                if associated_data == fail_id:
                    raise TokenDecryptError("No se pudo leer el token de Instagram")
                return super().decrypt(encrypted, associated_data=associated_data)

        job = CaptureInstagramFollowers(
            graph,
            connections,
            snapshots,
            DecryptFailCipher(),
            clock=lambda: NOW,
        )
        graph.followers = 2000
        result = job.execute_all()

        assert result.captured == 1
        assert result.failed == 1
        assert result.needs_reconnect == 0
        assert any(
            snap.instagram_account_id.value == "17841411111111111"
            for snap in snapshots.snapshots
        )

    def test_refreshes_token_near_expiry(self):
        graph, connections, snapshots, cipher, capture, complete, start = _wired(
            NOW
        )
        graph.expires_at = NOW + timedelta(days=3)
        complete.execute(OWNER_ID, start.execute(OWNER_ID).removeprefix(AUTH_URL), "code")
        graph.fetch_profile_tokens.clear()

        capture.execute_for_owner(OWNER_ID)

        stored = connections.get_by_owner(OWNER_ID)
        assert stored is not None
        assert stored.access_token_encrypted == (
            f"enc:{stored.connection.id.value}:ig-refreshed-token"
        )
        assert graph.fetch_profile_tokens == ["ig-refreshed-token"]
        assert ACCESS_TOKEN not in graph.fetch_profile_tokens

    def test_updates_username_and_avatar_on_capture(self):
        graph, connections, snapshots, _, capture, complete, start = _wired(NOW)
        complete.execute(OWNER_ID, start.execute(OWNER_ID).removeprefix(AUTH_URL), "code")
        graph.username = "luna.nueva"
        graph.avatar_url = (
            "https://scontent.cdninstagram.com/v/t51.2885-19/fresh.jpg"
        )

        capture.execute_for_owner(OWNER_ID)

        stored = connections.get_by_owner(OWNER_ID)
        assert stored is not None
        assert stored.connection.account.username.value == "luna.nueva"
        assert stored.connection.account.avatar_url is not None
        assert stored.connection.account.avatar_url.value.endswith("/fresh.jpg")
