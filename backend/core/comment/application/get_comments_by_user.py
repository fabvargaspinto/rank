from core.comment.domain.comment_page import CommentCursor, CommentPage
from core.comment.domain.comment_repo import CommentRepository
from core.shared.domain.user_id import UserId
from core.user.application.application_error import UserNotFoundError
from core.user.domain.user_repo import UserRepository

DEFAULT_LIMIT = 20
MAX_LIMIT = 50


class GetCommentsByUser:
    def __init__(
        self,
        user_repo: UserRepository,
        comment_repo: CommentRepository,
    ):
        self.user_repo = user_repo
        self.comment_repo = comment_repo

    def execute(
        self,
        user_id: str,
        limit: int = DEFAULT_LIMIT,
        cursor: str | None = None,
    ) -> CommentPage:
        UserId(user_id)
        user = self.user_repo.get_user(user_id)
        if user is None:
            raise UserNotFoundError("El usuario no existe")

        safe_limit = min(max(limit, 1), MAX_LIMIT)
        position = CommentCursor.decode(cursor) if cursor else None
        rows = self.comment_repo.get_comments_by_user_id(
            user.id.value,
            limit=safe_limit + 1,
            cursor=position,
        )
        has_more = len(rows) > safe_limit
        items = rows[:safe_limit]
        next_cursor = (
            CommentCursor.from_comment(items[-1]).encode()
            if has_more and items
            else None
        )
        return CommentPage(items=items, next_cursor=next_cursor)
