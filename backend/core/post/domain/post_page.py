from dataclasses import dataclass

from core.post.domain.post import Post
from core.post.domain.post_created_at import PostCreatedAt
from core.post.domain.post_error import InvalidPostCursorError
from core.post.domain.post_id import PostId


@dataclass(frozen=True)
class PostCursor:
    created_at: str
    id: str

    def encode(self) -> str:
        return f"{self.created_at}|{self.id}"

    @classmethod
    def decode(cls, value: str) -> "PostCursor":
        created_at, separator, post_id = value.rpartition("|")
        if not separator or not created_at or not post_id:
            raise InvalidPostCursorError("El cursor no es válido")
        try:
            normalized = PostCreatedAt.from_isoformat(created_at).to_isoformat()
            PostId(post_id)
        except Exception as exc:
            raise InvalidPostCursorError("El cursor no es válido") from exc
        return cls(created_at=normalized, id=post_id)

    @classmethod
    def from_post(cls, post: Post) -> "PostCursor":
        return cls(
            created_at=post.created_at.to_isoformat(),
            id=post.id.value,
        )


@dataclass(frozen=True)
class PostPage:
    items: list[Post]
    next_cursor: str | None
