from typing import Protocol

from core.post.domain.post import Post
from core.post.domain.post_page import PostCursor


class PostRepository(Protocol):
    def create_post(self, post: Post) -> Post:
        pass

    def get_posts_by_user_id(
        self,
        user_id: str,
        limit: int,
        cursor: PostCursor | None = None,
    ) -> list[Post]:
        pass

    def get_post(self, post_id: str) -> Post | None:
        pass

    def delete_post(self, post_id: str) -> None:
        pass
