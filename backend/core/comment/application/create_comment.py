from core.comment.domain.comment import Comment
from core.comment.domain.comment_repo import CommentRepository
from core.user.domain.user import User


class CreateComment:
    def __init__(self, comment_repo: CommentRepository):
        self.comment_repo = comment_repo

    def execute(
        self,
        user: User,
        text: str,
        link: str | None = None,
    ) -> Comment:
        comment = Comment.create(
            user_id=user.id.value,
            text=text,
            link=link,
        )
        return self.comment_repo.create_comment(comment)
