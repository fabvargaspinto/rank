from core.instagram.application.capture_instagram_followers import (
    CaptureInstagramFollowers,
    CaptureJobResult,
)
from core.instagram.application.ports import TokenCipher
from core.instagram.domain.follower_snapshot_repo import FollowerSnapshotRepository
from core.instagram.domain.instagram_connection_repo import (
    InstagramConnectionRepository,
)
from core.instagram.domain.instagram_graph import InstagramGraph


def run_weekly_snapshots(
    graph: InstagramGraph,
    connections: InstagramConnectionRepository,
    snapshots: FollowerSnapshotRepository,
    cipher: TokenCipher,
) -> CaptureJobResult:
    return CaptureInstagramFollowers(
        graph,
        connections,
        snapshots,
        cipher,
    ).execute_all()
