from core.comment.application.application_error import CommentNotFoundError
from core.comment.domain.comment_repo import CommentRepository
from core.user.application.application_error import UserNotFoundError
from core.user.domain.user_repo import UserRepository


class DeleteComment:
    def __init__(
        self,
        user_repo: UserRepository,
        comment_repo: CommentRepository,
    ):
        self.user_repo = user_repo
        self.comment_repo = comment_repo

    def execute(self, auth_id: str, comment_id: str) -> None:
        user = self.user_repo.get_user_by_auth_id(auth_id)
        if user is None:
            raise UserNotFoundError("El usuario no existe")

        comment = self.comment_repo.get_comment(comment_id)
        if comment is None or comment.user_id != user.id:
            raise CommentNotFoundError("La publicación no existe")

        self.comment_repo.delete_comment(comment_id)
