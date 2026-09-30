from dataclasses import dataclass
from datetime import datetime

from core.instagram.domain.errors import SnapshotWeekMismatchError
from core.instagram.domain.followers_count import FollowersCount
from core.instagram.domain.instagram_account_id import InstagramAccountId
from core.instagram.domain.snapshot_captured_at import SnapshotCapturedAt
from core.instagram.domain.snapshot_id import SnapshotId
from core.instagram.domain.week_start import WeekStart


@dataclass(frozen=True)
class FollowerSnapshot:
    id: SnapshotId
    instagram_account_id: InstagramAccountId
    followers_count: FollowersCount
    week_start: WeekStart
    captured_at: SnapshotCapturedAt

    @staticmethod
    def capture(
        instagram_account_id: str,
        followers_count: int,
        captured_at: datetime | None = None,
    ) -> "FollowerSnapshot":
        captured = (
            SnapshotCapturedAt(captured_at)
            if captured_at is not None
            else SnapshotCapturedAt.now()
        )
        return FollowerSnapshot(
            id=SnapshotId.generate(),
            instagram_account_id=InstagramAccountId(instagram_account_id),
            followers_count=FollowersCount(followers_count),
            week_start=WeekStart.from_datetime(captured.value),
            captured_at=captured,
        )

    def same_week_as(self, other: "FollowerSnapshot") -> bool:
        return (
            self.instagram_account_id == other.instagram_account_id
            and self.week_start == other.week_start
        )

    def replace_count(
        self,
        followers_count: int,
        captured_at: datetime | None = None,
    ) -> "FollowerSnapshot":
        captured = (
            SnapshotCapturedAt(captured_at)
            if captured_at is not None
            else SnapshotCapturedAt.now()
        )
        week_start = WeekStart.from_datetime(captured.value)
        if week_start != self.week_start:
            raise SnapshotWeekMismatchError(
                "La captura no pertenece a la misma semana"
            )
        return FollowerSnapshot(
            id=self.id,
            instagram_account_id=self.instagram_account_id,
            followers_count=FollowersCount(followers_count),
            week_start=self.week_start,
            captured_at=captured,
        )
