from typing import Protocol

from core.comment.domain.comment import Comment
from core.comment.domain.comment_page import CommentCursor


class CommentRepository(Protocol):
    def create_comment(self, comment: Comment) -> Comment:
        pass

    def get_comments_by_user_id(
        self,
        user_id: str,
        limit: int,
        cursor: CommentCursor | None = None,
    ) -> list[Comment]:
        pass

    def get_comment(self, comment_id: str) -> Comment | None:
        pass

    def delete_comment(self, comment_id: str) -> None:
        pass
