from datetime import date
from typing import Protocol

from core.instagram.domain.follower_snapshot import FollowerSnapshot


class FollowerSnapshotRepository(Protocol):
    def save(self, snapshot: FollowerSnapshot) -> FollowerSnapshot:
        pass

    def get_by_account_and_week(
        self,
        instagram_account_id: str,
        week_start: date,
    ) -> FollowerSnapshot | None:
        pass

    def list_by_account(self, instagram_account_id: str) -> list[FollowerSnapshot]:
        pass

    def delete_by_account(self, instagram_account_id: str) -> None:
        pass
