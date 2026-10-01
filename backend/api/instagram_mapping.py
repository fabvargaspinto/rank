from api.schemas.instagram import (
    FollowerHistoryItemResponse,
    FollowerHistoryResponse,
    InstagramConnectionResponse,
)
from core.instagram.application.get_follower_history import FollowerHistoryPoint
from core.instagram.application.get_instagram_connection import InstagramConnectionView


def to_instagram_connection_response(
    view: InstagramConnectionView,
) -> InstagramConnectionResponse:
    return InstagramConnectionResponse(
        connected=view.connected,
        username=view.username,
        instagram_account_id=view.instagram_account_id,
        avatar_url=view.avatar_url,
        followers_count=view.followers_count,
        followers_delta=view.followers_delta,
    )


def to_follower_history_response(
    points: list[FollowerHistoryPoint],
) -> FollowerHistoryResponse:
    return FollowerHistoryResponse(
        items=[
            FollowerHistoryItemResponse(
                week_start=point.week_start,
                followers_count=point.followers_count,
                captured_at=point.captured_at,
                delta=point.delta,
            )
            for point in points
        ]
    )
