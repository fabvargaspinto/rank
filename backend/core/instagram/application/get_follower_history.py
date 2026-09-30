from dataclasses import dataclass
from datetime import date, datetime

from core.instagram.application.application_error import InstagramNotConnectedError
from core.instagram.domain.follower_snapshot_repo import FollowerSnapshotRepository
from core.instagram.domain.instagram_connection_repo import (
    InstagramConnectionRepository,
)


@dataclass(frozen=True)
class FollowerHistoryPoint:
    week_start: date
    followers_count: int
    captured_at: datetime
    delta: int | None


class GetFollowerHistory:
    def __init__(
        self,
        connections: InstagramConnectionRepository,
        snapshots: FollowerSnapshotRepository,
    ) -> None:
        self._connections = connections
        self._snapshots = snapshots

    def execute(self, owner_user_id: str) -> list[FollowerHistoryPoint]:
        stored = self._connections.get_by_owner(owner_user_id)
        if stored is None or not stored.connection.belongs_to(owner_user_id):
            raise InstagramNotConnectedError("No hay una cuenta de Instagram conectada")

        points: list[FollowerHistoryPoint] = []
        previous_count: int | None = None
        for snapshot in self._snapshots.list_by_account(
            stored.connection.account.id.value
        ):
            count = snapshot.followers_count.value
            points.append(
                FollowerHistoryPoint(
                    week_start=snapshot.week_start.value,
                    followers_count=count,
                    captured_at=snapshot.captured_at.value,
                    delta=None if previous_count is None else count - previous_count,
                )
            )
            previous_count = count
        return points
