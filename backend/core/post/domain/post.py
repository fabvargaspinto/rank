from dataclasses import dataclass

from core.post.domain.post_created_at import PostCreatedAt
from core.post.domain.post_id import PostId
from core.post.domain.post_link import PostLink
from core.post.domain.post_text import PostText
from core.shared.domain.user_id import UserId


@dataclass(frozen=True)
class Post:
    id: PostId
    user_id: UserId
    text: PostText
    link: PostLink | None
    created_at: PostCreatedAt

    @staticmethod
    def create(
        user_id: str,
        text: str,
        link: str | None = None,
    ) -> "Post":
        return Post(
            id=PostId.generate(),
            user_id=UserId(user_id),
            text=PostText(text),
            link=PostLink(link) if link else None,
            created_at=PostCreatedAt.now(),
        )
