from core.post.domain.post import Post
from core.post.domain.post_page import PostCursor
from core.post.domain.post_repo import PostRepository


class FakePostRepo(PostRepository):
    def __init__(self) -> None:
        self.posts: list[Post] = []

    def create_post(self, post: Post) -> Post:
        self.posts.append(post)
        return post

    def get_posts_by_user_id(
        self,
        user_id: str,
        limit: int,
        cursor: PostCursor | None = None,
    ) -> list[Post]:
        if limit <= 0:
            return []

        matching = [
            post
            for post in self.posts
            if post.user_id.value == user_id
        ]
        matching.sort(
            key=lambda post: (
                post.created_at.to_isoformat(),
                post.id.value,
            ),
            reverse=True,
        )
        if cursor is not None:
            position = (cursor.created_at, cursor.id)
            matching = [
                post
                for post in matching
                if (post.created_at.to_isoformat(), post.id.value) < position
            ]
        return matching[:limit]

    def get_post(self, post_id: str) -> Post | None:
        for post in self.posts:
            if post.id.value == post_id:
                return post
        return None

    def delete_post(self, post_id: str) -> None:
        self.posts = [
            post for post in self.posts if post.id.value != post_id
        ]
