from core.comment.application.application_error import CommentNotFoundError
from core.comment.domain.comment_id import CommentId
from core.comment.domain.comment_repo import CommentRepository
from core.user.domain.user import User


class DeleteComment:
    def __init__(self, comment_repo: CommentRepository):
        self.comment_repo = comment_repo

    def execute(self, user: User, comment_id: str) -> None:
        CommentId(comment_id)
        comment = self.comment_repo.get_comment(comment_id)
        if comment is None or comment.user_id != user.id:
            raise CommentNotFoundError("La publicación no existe")

        self.comment_repo.delete_comment(comment_id)
