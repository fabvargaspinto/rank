from datetime import UTC, datetime, timedelta

from core.instagram.application.capture_instagram_followers import (
    CaptureInstagramFollowers,
)
from core.instagram.domain.instagram_connection import InstagramConnection
from core.instagram.domain.instagram_connection_repo import StoredInstagramConnection
from core.instagram.infrastructure.follower_snapshot_sql_repo import (
    FollowerSnapshotSqlRepo,
)
from core.instagram.infrastructure.instagram_connection_sql_repo import (
    InstagramConnectionSqlRepo,
)
from core.instagram.infrastructure.sqlite_db import SqliteDatabase
from tests.unit.instagram.application.fakes import FakeInstagramGraph, FakeTokenCipher

OWNER_ID = "550e8400-e29b-41d4-a716-446655440000"
ACCOUNT_ID = "17841400000000000"
NOW = datetime(2026, 10, 7, 12, 0, tzinfo=UTC)


def test_weekly_capture_against_sqlite_is_idempotent():
    db = SqliteDatabase(":memory:")
    connections = InstagramConnectionSqlRepo(db)
    snapshots = FollowerSnapshotSqlRepo(db)
    graph = FakeInstagramGraph()
    graph.followers = 1250
    cipher = FakeTokenCipher()
    connection = InstagramConnection.connect(
        OWNER_ID,
        ACCOUNT_ID,
        "luna.reyes",
        NOW + timedelta(days=40),
    )
    connections.save(
        StoredInstagramConnection(
            connection,
            cipher.encrypt("ig-token", associated_data=connection.id.value),
        )
    )
    capture = CaptureInstagramFollowers(
        graph,
        connections,
        snapshots,
        cipher,
        clock=lambda: NOW,
    )

    first = capture.execute_for_owner(OWNER_ID)
    graph.followers = 1280
    second = capture.execute_for_owner(OWNER_ID)

    history = snapshots.list_by_account(ACCOUNT_ID)
    assert first.id == second.id
    assert len(history) == 1
    assert history[0].followers_count.value == 1280
    assert history[0].week_start.value.isoformat() == "2026-10-05"
