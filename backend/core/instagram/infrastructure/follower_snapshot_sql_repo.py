from datetime import date

from core.instagram.domain.follower_snapshot import FollowerSnapshot
from core.instagram.domain.follower_snapshot_repo import FollowerSnapshotRepository
from core.instagram.infrastructure.snapshot_mapper import SnapshotMapper
from core.instagram.infrastructure.sql import SqlDatabase

_SAVE_SQL = """
INSERT INTO follower_snapshots (
    id,
    instagram_account_id,
    followers_count,
    week_start,
    captured_at
) VALUES (?, ?, ?, ?, ?)
ON CONFLICT(instagram_account_id, week_start) DO UPDATE SET
    followers_count = excluded.followers_count,
    captured_at = excluded.captured_at
"""


class FollowerSnapshotSqlRepo(FollowerSnapshotRepository):
    def __init__(self, db: SqlDatabase) -> None:
        self._db = db
        self._mapper = SnapshotMapper()

    def save(self, snapshot: FollowerSnapshot) -> FollowerSnapshot:
        self._db.execute(_SAVE_SQL, self._mapper.to_row(snapshot))
        stored = self.get_by_account_and_week(
            snapshot.instagram_account_id.value,
            snapshot.week_start.value,
        )
        return stored if stored is not None else snapshot

    def get_by_account_and_week(
        self,
        instagram_account_id: str,
        week_start: date,
    ) -> FollowerSnapshot | None:
        rows = self._db.execute(
            """
            SELECT * FROM follower_snapshots
            WHERE instagram_account_id = ? AND week_start = ?
            LIMIT 1
            """,
            (instagram_account_id, week_start.isoformat()),
        )
        if not rows:
            return None
        return self._mapper.to_domain(rows[0])

    def list_by_account(self, instagram_account_id: str) -> list[FollowerSnapshot]:
        rows = self._db.execute(
            """
            SELECT * FROM follower_snapshots
            WHERE instagram_account_id = ?
            ORDER BY week_start ASC
            """,
            (instagram_account_id,),
        )
        return [self._mapper.to_domain(row) for row in rows]

    def delete_by_account(self, instagram_account_id: str) -> None:
        self._db.execute(
            "DELETE FROM follower_snapshots WHERE instagram_account_id = ?",
            (instagram_account_id,),
        )
