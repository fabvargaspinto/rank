from secrets import token_urlsafe
from urllib.parse import urlsplit

from core.instagram.domain.follower_snapshot_repo import FollowerSnapshotRepository
from core.instagram.domain.instagram_connection_repo import (
    InstagramConnectionRepository,
)


class DeleteInstagramUserData:
    """Borra conexión y snapshots por Instagram account id (callbacks de Meta)."""

    def __init__(
        self,
        connections: InstagramConnectionRepository,
        snapshots: FollowerSnapshotRepository,
    ) -> None:
        self._connections = connections
        self._snapshots = snapshots

    def execute(self, instagram_account_id: str) -> str:
        stored = self._connections.get_by_account(instagram_account_id)
        if stored is not None:
            account_id = stored.connection.account.id.value
            self._snapshots.delete_by_account(account_id)
            self._connections.delete_by_owner(stored.connection.owner_user_id.value)
        return token_urlsafe(16)


def public_site_origin(redirect_uri: str) -> str:
    parts = urlsplit(redirect_uri.strip())
    if not parts.scheme or not parts.netloc:
        raise ValueError("INSTAGRAM_REDIRECT_URI inválida")
    return f"{parts.scheme}://{parts.netloc}"
