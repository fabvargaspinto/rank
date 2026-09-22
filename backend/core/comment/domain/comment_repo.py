from typing import Protocol

from core.comment.domain.comment import Comment


class CommentRepository(Protocol):
    def create_comment(self, comment: Comment) -> Comment:
        pass

    def get_comments_by_user_id(
        self,
        user_id: str,
        limit: int,
        offset: int,
    ) -> list[Comment]:
        pass
