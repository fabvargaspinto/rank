from dataclasses import dataclass

from core.comment.domain.comment import Comment
from core.comment.domain.comment_created_at import CommentCreatedAt
from core.comment.domain.comment_error import InvalidCommentCursorError
from core.comment.domain.comment_id import CommentId


@dataclass(frozen=True)
class CommentCursor:
    created_at: str
    id: str

    def encode(self) -> str:
        return f"{self.created_at}|{self.id}"

    @classmethod
    def decode(cls, value: str) -> "CommentCursor":
        created_at, separator, comment_id = value.rpartition("|")
        if not separator or not created_at or not comment_id:
            raise InvalidCommentCursorError("El cursor no es válido")
        try:
            CommentCreatedAt.from_isoformat(created_at)
            CommentId(comment_id)
        except Exception as exc:
            raise InvalidCommentCursorError("El cursor no es válido") from exc
        return cls(created_at=created_at, id=comment_id)

    @classmethod
    def from_comment(cls, comment: Comment) -> "CommentCursor":
        return cls(
            created_at=comment.created_at.to_isoformat(),
            id=comment.id.value,
        )


@dataclass(frozen=True)
class CommentPage:
    items: list[Comment]
    next_cursor: str | None
