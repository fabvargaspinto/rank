from core.instagram.application.application_error import InstagramNotConnectedError
from core.instagram.domain.follower_snapshot_repo import FollowerSnapshotRepository
from core.instagram.domain.instagram_connection_repo import (
    InstagramConnectionRepository,
)


class DisconnectInstagram:
    def __init__(
        self,
        connections: InstagramConnectionRepository,
        snapshots: FollowerSnapshotRepository,
    ) -> None:
        self._connections = connections
        self._snapshots = snapshots

    def execute(self, owner_user_id: str) -> None:
        stored = self._connections.get_by_owner(owner_user_id)
        if stored is None or not stored.connection.belongs_to(owner_user_id):
            raise InstagramNotConnectedError("No hay una cuenta de Instagram conectada")

        self._snapshots.delete_by_account(stored.connection.account.id.value)
        self._connections.delete_by_owner(owner_user_id)
