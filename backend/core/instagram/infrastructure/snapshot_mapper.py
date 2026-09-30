from core.instagram.domain.follower_snapshot import FollowerSnapshot
from core.instagram.domain.followers_count import FollowersCount
from core.instagram.domain.instagram_account_id import InstagramAccountId
from core.instagram.domain.snapshot_captured_at import SnapshotCapturedAt
from core.instagram.domain.snapshot_id import SnapshotId
from core.instagram.domain.week_start import WeekStart
from core.instagram.infrastructure.error_infrastructure import InstagramDbError


class SnapshotMapper:
    def to_domain(self, row: dict[str, object]) -> FollowerSnapshot:
        return FollowerSnapshot(
            id=SnapshotId(str(row["id"])),
            instagram_account_id=InstagramAccountId(str(row["instagram_account_id"])),
            followers_count=FollowersCount(_followers_count(row["followers_count"])),
            week_start=WeekStart.from_isoformat(str(row["week_start"])),
            captured_at=SnapshotCapturedAt.from_isoformat(str(row["captured_at"])),
        )

    def to_row(self, snapshot: FollowerSnapshot) -> tuple[object, ...]:
        return (
            snapshot.id.value,
            snapshot.instagram_account_id.value,
            snapshot.followers_count.value,
            snapshot.week_start.to_isoformat(),
            snapshot.captured_at.to_isoformat(),
        )


def _followers_count(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        if isinstance(value, str) and value.strip().isdigit():
            return int(value.strip())
        raise InstagramDbError("No se pudo leer el historial de followers")
    return value
