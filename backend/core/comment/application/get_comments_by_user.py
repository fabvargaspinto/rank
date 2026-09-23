from core.comment.domain.comment import Comment
from core.comment.domain.comment_repo import CommentRepository
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
        offset: int = 0,
    ) -> list[Comment]:
        user = self.user_repo.get_user(user_id)
        if user is None:
            raise UserNotFoundError("El usuario no existe")

        safe_limit = min(max(limit, 0), MAX_LIMIT)
        safe_offset = max(offset, 0)

        return self.comment_repo.get_comments_by_user_id(
            user.id.value,
            limit=safe_limit,
            offset=safe_offset,
        )
