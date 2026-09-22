from core.comment.domain.comment import Comment
from core.comment.domain.comment_created_at import CommentCreatedAt
from core.comment.domain.comment_id import CommentId
from core.comment.domain.comment_link import CommentLink
from core.comment.domain.comment_text import CommentText
from core.user.domain.user_id import UserId


class CommentMapper:
    def to_domain(self, row: dict) -> Comment:
        return Comment(
            id=CommentId(row["id"]),
            user_id=UserId(row["user_id"]),
            text=CommentText(str(row["text"])),
            link=self._optional_link(row.get("link")),
            created_at=CommentCreatedAt.from_isoformat(row["created_at"]),
        )

    def to_row(self, comment: Comment) -> dict:
        return {
            "id": comment.id.value,
            "user_id": comment.user_id.value,
            "text": comment.text.value,
            "link": comment.link.value if comment.link else None,
            "created_at": comment.created_at.to_isoformat(),
        }

    def _optional_link(self, value: object) -> CommentLink | None:
        if not isinstance(value, str) or not value.strip():
            return None
        return CommentLink(value)
