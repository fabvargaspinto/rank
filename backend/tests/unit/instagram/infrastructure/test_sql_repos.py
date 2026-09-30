from datetime import UTC, datetime

from core.instagram.domain.follower_snapshot import FollowerSnapshot
from core.instagram.domain.instagram_connection import InstagramConnection
from core.instagram.domain.instagram_connection_repo import StoredInstagramConnection
from core.instagram.infrastructure.follower_snapshot_sql_repo import (
    FollowerSnapshotSqlRepo,
)
from core.instagram.infrastructure.instagram_connection_sql_repo import (
    InstagramConnectionSqlRepo,
)
from core.instagram.infrastructure.sqlite_db import SqliteDatabase

OWNER_ID = "550e8400-e29b-41d4-a716-446655440000"
ACCOUNT_ID = "17841400000000000"
NOW = datetime(2026, 10, 7, 12, 0, tzinfo=UTC)


def _repos() -> tuple[InstagramConnectionSqlRepo, FollowerSnapshotSqlRepo]:
    db = SqliteDatabase(":memory:")
    return InstagramConnectionSqlRepo(db), FollowerSnapshotSqlRepo(db)


def test_connection_round_trip_does_not_store_plain_token():
    connections, _ = _repos()
    stored = StoredInstagramConnection(
        InstagramConnection.connect(
            OWNER_ID,
            ACCOUNT_ID,
            "luna.reyes",
            NOW,
        ),
        "enc:ig-token",
    )

    connections.save(stored)
    loaded = connections.get_by_owner(OWNER_ID)

    assert loaded is not None
    assert loaded.connection.account.username.value == "luna.reyes"
    assert loaded.access_token_encrypted == "enc:ig-token"
    assert connections.get_by_account(ACCOUNT_ID) is not None


def test_snapshot_upsert_is_idempotent_for_the_same_week():
    _, snapshots = _repos()
    first = FollowerSnapshot.capture(ACCOUNT_ID, 1250, NOW)
    snapshots.save(first)
    snapshots.save(first.replace_count(1260, NOW))

    history = snapshots.list_by_account(ACCOUNT_ID)

    assert len(history) == 1
    assert history[0].id == first.id
    assert history[0].followers_count.value == 1260


def test_delete_connection_and_snapshots():
    connections, snapshots = _repos()
    stored = StoredInstagramConnection(
        InstagramConnection.connect(OWNER_ID, ACCOUNT_ID, "luna", NOW),
        "enc:token",
    )
    connections.save(stored)
    snapshots.save(FollowerSnapshot.capture(ACCOUNT_ID, 100, NOW))

    snapshots.delete_by_account(ACCOUNT_ID)
    connections.delete_by_owner(OWNER_ID)

    assert connections.get_by_owner(OWNER_ID) is None
    assert snapshots.list_by_account(ACCOUNT_ID) == []
