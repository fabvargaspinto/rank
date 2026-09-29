from core.post.domain.post_page import PostCursor, PostPage
from core.post.domain.post_repo import PostRepository
from core.shared.domain.user_id import UserId
from core.user.application.application_error import UserNotFoundError
from core.user.domain.user_repo import UserRepository

DEFAULT_LIMIT = 20
MAX_LIMIT = 50


class GetPostsByUser:
    def __init__(
        self,
        user_repo: UserRepository,
        post_repo: PostRepository,
    ):
        self.user_repo = user_repo
        self.post_repo = post_repo

    def execute(
        self,
        user_id: str,
        limit: int = DEFAULT_LIMIT,
        cursor: str | None = None,
    ) -> PostPage:
        UserId(user_id)
        user = self.user_repo.get_user(user_id)
        if user is None:
            raise UserNotFoundError("El usuario no existe")

        safe_limit = min(max(limit, 1), MAX_LIMIT)
        position = PostCursor.decode(cursor) if cursor else None
        rows = self.post_repo.get_posts_by_user_id(
            user.id.value,
            limit=safe_limit + 1,
            cursor=position,
        )
        has_more = len(rows) > safe_limit
        items = rows[:safe_limit]
        next_cursor = (
            PostCursor.from_post(items[-1]).encode()
            if has_more and items
            else None
        )
        return PostPage(items=items, next_cursor=next_cursor)
