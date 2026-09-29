from core.post.domain.post import Post
from core.post.domain.post_created_at import PostCreatedAt
from core.post.domain.post_id import PostId
from core.post.domain.post_link import PostLink
from core.post.domain.post_text import PostText
from core.shared.domain.user_id import UserId


class PostMapper:
    def to_domain(self, row: dict) -> Post:
        return Post(
            id=PostId(row["id"]),
            user_id=UserId(row["user_id"]),
            text=PostText(str(row["text"])),
            link=self._optional_link(row.get("link")),
            created_at=PostCreatedAt.from_isoformat(row["created_at"]),
        )

    def to_row(self, post: Post) -> dict:
        return {
            "id": post.id.value,
            "user_id": post.user_id.value,
            "text": post.text.value,
            "link": post.link.value if post.link else None,
            "created_at": post.created_at.to_isoformat(),
        }

    def _optional_link(self, value: object) -> PostLink | None:
        if not isinstance(value, str) or not value.strip():
            return None
        return PostLink(value)
