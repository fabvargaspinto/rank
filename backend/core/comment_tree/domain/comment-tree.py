from datetime import datetime

from backend.core.comment_tree.domain.comment_id import CommentId
from backend.core.comment_tree.domain.comment_title import CommentTitle
from backend.core.comment_tree.domain.comment_description import CommentDescription
from backend.core.comment_tree.domain.comment_link_url import CommentLinkUrl
from backend.core.comment_tree.domain.comment_created_at import CommentCreatedAt
from backend.core.user.domain.user_id import UserId
from dataclasses import dataclass

@dataclass(frozen=True)
class CommentTree:
    comment_id: CommentId
    user_id: UserId
    title: CommentTitle
    description: CommentDescription
    link_url: CommentLinkUrl
    created_at: CommentCreatedAt

    @classmethod
    def create(cls,
      user_id: UserId,
      title: CommentTitle,
      description: CommentDescription,
      link_url: CommentLinkUrl,
      created_at: CommentCreatedAt
      ):
        return cls(
            comment_id=CommentId.generate(),
            user_id=user_id,
            title=title,
            description=description,
            link_url=link_url,
            created_at=created_at
        )

    @classmethod
    def from_primitives(cls, comment_id: int, user_id: int, title: str, description: str, link_url: str, created_at: datetime):
        return cls(
            comment_id=CommentId(comment_id),
            user_id=UserId(user_id),
            title=CommentTitle(title),
            description=CommentDescription(description),
            link_url=CommentLinkUrl(link_url),
            created_at=CommentCreatedAt(created_at)
        )

    def to_primitives(self):
        return {
            "comment_id": self.comment_id.value,
            "user_id": self.user_id.value,
            "title": self.title.value,
            "description": self.description.value,
            "link_url": self.link_url.value,
            "created_at": self.created_at.value
        }