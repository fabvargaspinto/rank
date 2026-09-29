from dataclasses import dataclass

from core.post.application.get_posts_by_user import (
    DEFAULT_LIMIT,
    GetPostsByUser,
)
from core.post.domain.post import Post
from core.user.application.get_user_by_name import GetUserByName
from core.user.domain.user import User


@dataclass(frozen=True)
class PublicProfile:
    user: User
    posts: list[Post]
    next_cursor: str | None


class GetPublicProfile:
    def __init__(
        self,
        get_user_by_name: GetUserByName,
        get_posts_by_user: GetPostsByUser,
    ):
        self.get_user_by_name = get_user_by_name
        self.get_posts_by_user = get_posts_by_user

    def execute(self, name: str, limit: int = DEFAULT_LIMIT) -> PublicProfile:
        user = self.get_user_by_name.execute(name)
        page = self.get_posts_by_user.execute(user.id.value, limit=limit)
        return PublicProfile(
            user=user,
            posts=page.items,
            next_cursor=page.next_cursor,
        )
