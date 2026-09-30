from dataclasses import dataclass

from core.instagram.domain.follower_snapshot_repo import FollowerSnapshotRepository
from core.instagram.domain.instagram_connection_repo import (
    InstagramConnectionRepository,
)


@dataclass(frozen=True)
class InstagramConnectionView:
    connected: bool
    username: str | None
    instagram_account_id: str | None
    followers_count: int | None
    previous_followers_count: int | None

    @property
    def followers_delta(self) -> int | None:
        if self.followers_count is None or self.previous_followers_count is None:
            return None
        return self.followers_count - self.previous_followers_count


class GetInstagramConnection:
    def __init__(
        self,
        connections: InstagramConnectionRepository,
        snapshots: FollowerSnapshotRepository,
    ) -> None:
        self._connections = connections
        self._snapshots = snapshots

    def execute(self, owner_user_id: str) -> InstagramConnectionView:
        stored = self._connections.get_by_owner(owner_user_id)
        if stored is None or not stored.connection.belongs_to(owner_user_id):
            return InstagramConnectionView(
                connected=False,
                username=None,
                instagram_account_id=None,
                followers_count=None,
                previous_followers_count=None,
            )

        history = self._snapshots.list_by_account(stored.connection.account.id.value)
        latest = history[-1] if history else None
        previous = history[-2] if len(history) > 1 else None
        return InstagramConnectionView(
            connected=True,
            username=stored.connection.account.username.value,
            instagram_account_id=stored.connection.account.id.value,
            followers_count=latest.followers_count.value if latest else None,
            previous_followers_count=(
                previous.followers_count.value if previous else None
            ),
        )
