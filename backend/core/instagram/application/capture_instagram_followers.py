from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from logging import getLogger

from core.instagram.application.application_error import (
    InstagramGraphError,
    InstagramNotConnectedError,
    InstagramTokenExpiredError,
)
from core.instagram.application.ports import TokenCipher
from core.instagram.domain.follower_snapshot import FollowerSnapshot
from core.instagram.domain.follower_snapshot_repo import FollowerSnapshotRepository
from core.instagram.domain.instagram_connection_repo import (
    InstagramConnectionRepository,
    StoredInstagramConnection,
)
from core.instagram.domain.instagram_graph import InstagramGraph
from core.shared.application.application_error import ApplicationError
from core.shared.domain.domain_error import DomainError

logger = getLogger("ig.instagram.snapshots")

_REFRESH_WINDOW = timedelta(days=7)


@dataclass(frozen=True)
class CaptureJobResult:
    captured: int
    failed: int


class CaptureInstagramFollowers:
    def __init__(
        self,
        graph: InstagramGraph,
        connections: InstagramConnectionRepository,
        snapshots: FollowerSnapshotRepository,
        cipher: TokenCipher,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._graph = graph
        self._connections = connections
        self._snapshots = snapshots
        self._cipher = cipher
        self._clock = clock or (lambda: datetime.now(UTC))

    def execute_for_owner(self, owner_user_id: str) -> FollowerSnapshot:
        stored = self._connections.get_by_owner(owner_user_id)
        if stored is None or not stored.connection.belongs_to(owner_user_id):
            raise InstagramNotConnectedError("No hay una cuenta de Instagram conectada")
        return self._capture(stored)

    def execute_all(self) -> CaptureJobResult:
        captured = 0
        failed = 0
        for stored in self._connections.list_all():
            try:
                self._capture(stored)
                captured += 1
            except (ApplicationError, DomainError):
                logger.warning(
                    "instagram_snapshot_failed",
                    extra={"owner_user_id": stored.connection.owner_user_id.value},
                )
                failed += 1
        return CaptureJobResult(captured=captured, failed=failed)

    def _capture(self, stored: StoredInstagramConnection) -> FollowerSnapshot:
        now = self._clock()
        access_token = self._cipher.decrypt(stored.access_token_encrypted)
        connection = stored.connection
        if connection.token_expires_at.value - now <= _REFRESH_WINDOW:
            try:
                refreshed = self._graph.refresh_access_token(access_token)
                access_token = refreshed.value
                connection = connection.with_token_expiry(refreshed.expires_at)
                self._connections.save(
                    StoredInstagramConnection(
                        connection=connection,
                        access_token_encrypted=self._cipher.encrypt(access_token),
                    )
                )
            except InstagramGraphError:
                logger.warning(
                    "instagram_token_refresh_failed",
                    extra={"owner_user_id": connection.owner_user_id.value},
                )

        if connection.token_is_expired(now):
            raise InstagramTokenExpiredError("El acceso a Instagram expiró")

        count = self._graph.fetch_followers(access_token)
        snapshot = FollowerSnapshot.capture(
            connection.account.id.value,
            count,
            now,
        )
        existing = self._snapshots.get_by_account_and_week(
            connection.account.id.value,
            snapshot.week_start.value,
        )
        if existing is None:
            return self._snapshots.save(snapshot)
        return self._snapshots.save(existing.replace_count(count, now))
