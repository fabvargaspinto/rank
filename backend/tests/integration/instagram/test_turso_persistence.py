from datetime import UTC, datetime, timedelta
from uuid import uuid4

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
from tests.unit.instagram.application.fakes import FakeInstagramGraph, FakeTokenCipher

NOW = datetime(2026, 10, 7, 12, 0, tzinfo=UTC)


def test_weekly_capture_against_turso_development_is_idempotent(turso_development_db):
    owner_id = str(uuid4())
    account_id = f"178414{uuid4().hex[:11]}"
    db = turso_development_db
    connections = InstagramConnectionSqlRepo(db)
    snapshots = FollowerSnapshotSqlRepo(db)
    graph = FakeInstagramGraph()
    graph.followers = 1250
    cipher = FakeTokenCipher()
    connection = InstagramConnection.connect(
        owner_id,
        account_id,
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

    try:
        first = capture.execute_for_owner(owner_id)
        graph.followers = 1280
        second = capture.execute_for_owner(owner_id)

        history = snapshots.list_by_account(account_id)
        assert first.id == second.id
        assert len(history) == 1
        assert history[0].followers_count.value == 1280
        assert history[0].week_start.value.isoformat() == "2026-10-05"
    finally:
        connections.delete_by_owner(owner_id)
        snapshots.delete_by_account(account_id)
