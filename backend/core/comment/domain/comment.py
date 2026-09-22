from dataclasses import dataclass

from core.comment.domain.comment_created_at import CommentCreatedAt
from core.comment.domain.comment_id import CommentId
from core.comment.domain.comment_link import CommentLink
from core.comment.domain.comment_text import CommentText
from core.user.domain.user_id import UserId


@dataclass(frozen=True)
class Comment:
    id: CommentId
    user_id: UserId
    text: CommentText
    link: CommentLink | None
    created_at: CommentCreatedAt

    @staticmethod
    def create(
        user_id: str,
        text: str,
        link: str | None = None,
    ) -> "Comment":
        return Comment(
            id=CommentId.generate(),
            user_id=UserId(user_id),
            text=CommentText(text),
            link=CommentLink(link) if link else None,
            created_at=CommentCreatedAt.now(),
        )
