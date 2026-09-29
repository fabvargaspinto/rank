from dataclasses import dataclass

from core.comment.application.get_comments_by_user import (
    DEFAULT_LIMIT,
    GetCommentsByUser,
)
from core.comment.domain.comment import Comment
from core.user.application.get_user_by_name import GetUserByName
from core.user.domain.user import User


@dataclass(frozen=True)
class PublicProfile:
    user: User
    comments: list[Comment]
    next_cursor: str | None


class GetPublicProfile:
    def __init__(
        self,
        get_user_by_name: GetUserByName,
        get_comments_by_user: GetCommentsByUser,
    ):
        self.get_user_by_name = get_user_by_name
        self.get_comments_by_user = get_comments_by_user

    def execute(self, name: str, limit: int = DEFAULT_LIMIT) -> PublicProfile:
        user = self.get_user_by_name.execute(name)
        page = self.get_comments_by_user.execute(user.id.value, limit=limit)
        return PublicProfile(
            user=user,
            comments=page.items,
            next_cursor=page.next_cursor,
        )
