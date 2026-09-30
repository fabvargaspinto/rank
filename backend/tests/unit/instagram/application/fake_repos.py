from datetime import date

from core.instagram.domain.follower_snapshot import FollowerSnapshot
from core.instagram.domain.follower_snapshot_repo import FollowerSnapshotRepository
from core.instagram.domain.instagram_connection_repo import (
    InstagramConnectionRepository,
    StoredInstagramConnection,
)


class FakeConnectionRepo(InstagramConnectionRepository):
    def __init__(self) -> None:
        self.by_owner: dict[str, StoredInstagramConnection] = {}
        self.by_account: dict[str, StoredInstagramConnection] = {}

    def save(self, stored: StoredInstagramConnection) -> StoredInstagramConnection:
        owner = stored.connection.owner_user_id.value
        previous = self.by_owner.get(owner)
        if previous is not None:
            self.by_account.pop(previous.connection.account.id.value, None)
        self.by_owner[owner] = stored
        self.by_account[stored.connection.account.id.value] = stored
        return stored

    def get_by_owner(self, owner_user_id: str) -> StoredInstagramConnection | None:
        return self.by_owner.get(owner_user_id)

    def get_by_account(
        self, instagram_account_id: str
    ) -> StoredInstagramConnection | None:
        return self.by_account.get(instagram_account_id)

    def list_all(self) -> list[StoredInstagramConnection]:
        return list(self.by_owner.values())

    def delete_by_owner(self, owner_user_id: str) -> None:
        stored = self.by_owner.pop(owner_user_id, None)
        if stored is not None:
            self.by_account.pop(stored.connection.account.id.value, None)


class FakeSnapshotRepo(FollowerSnapshotRepository):
    def __init__(self) -> None:
        self.snapshots: list[FollowerSnapshot] = []

    def save(self, snapshot: FollowerSnapshot) -> FollowerSnapshot:
        self.snapshots = [
            item
            for item in self.snapshots
            if not (
                item.instagram_account_id == snapshot.instagram_account_id
                and item.week_start == snapshot.week_start
            )
        ]
        self.snapshots.append(snapshot)
        self.snapshots.sort(key=lambda item: item.week_start.value)
        return snapshot

    def get_by_account_and_week(
        self,
        instagram_account_id: str,
        week_start: date,
    ) -> FollowerSnapshot | None:
        for snapshot in self.snapshots:
            if (
                snapshot.instagram_account_id.value == instagram_account_id
                and snapshot.week_start.value == week_start
            ):
                return snapshot
        return None

    def list_by_account(self, instagram_account_id: str) -> list[FollowerSnapshot]:
        matching = [
            snapshot
            for snapshot in self.snapshots
            if snapshot.instagram_account_id.value == instagram_account_id
        ]
        matching.sort(key=lambda item: item.week_start.value)
        return matching

    def delete_by_account(self, instagram_account_id: str) -> None:
        self.snapshots = [
            snapshot
            for snapshot in self.snapshots
            if snapshot.instagram_account_id.value != instagram_account_id
        ]
