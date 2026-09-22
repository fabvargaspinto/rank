from core.comment.domain.comment import Comment
from core.comment.domain.comment_repo import CommentRepository
from core.user.application.application_error import UserNotFoundError
from core.user.domain.user_repo import UserRepository


class CreateComment:
    def __init__(
        self,
        user_repo: UserRepository,
        comment_repo: CommentRepository,
    ):
        self.user_repo = user_repo
        self.comment_repo = comment_repo

    def execute(
        self,
        auth_id: str,
        text: str,
        link: str | None = None,
    ) -> Comment:
        user = self.user_repo.get_user_by_auth_id(auth_id)
        if user is None:
            raise UserNotFoundError("El usuario no existe")

        comment = Comment.create(
            user_id=user.id.value,
            text=text,
            link=link,
        )
        return self.comment_repo.create_comment(comment)
