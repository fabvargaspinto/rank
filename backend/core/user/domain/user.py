from dataclasses import dataclass

from core.user.domain.user_avatar_url import UserAvatarUrl
from core.user.domain.user_created_at import UserCreatedAt
from core.user.domain.user_description import UserDescription
from core.user.domain.user_id import UserId
from core.user.domain.user_name import UserName
from core.user.domain.user_updated_at import UserUpdatedAt


@dataclass(frozen=True)
class User:
    id: UserId
    name: UserName
    avatar_url: UserAvatarUrl | None
    description: UserDescription
    created_at: UserCreatedAt
    updated_at: UserUpdatedAt

    @classmethod
    def create(
        cls,
        name: UserName,
        avatar_url: UserAvatarUrl,
        description: UserDescription,
    ) -> "User":
        return cls(
            id=UserId.generate(),
            name=name,
            avatar_url=avatar_url,
            description=description,
            created_at=UserCreatedAt.generate(),
            updated_at=UserUpdatedAt.generate(),
        )
     
    def to_primitives(self):
        return {
            "id": self.id.value,
            "name": self.name.value,
            "avatar_url": self.avatar_url.value if self.avatar_url else None,
            "description": self.description.value,
            "created_at": self.created_at.value,
            "updated_at": self.updated_at.value
        }
        
    @classmethod
    def from_primitives(cls, id: str, name: str, avatar_url: str | None, description: str, created_at: str, updated_at: str) -> "User":
        return cls(
            id=UserId(id),
            name=UserName(name),
            avatar_url=UserAvatarUrl(avatar_url) if avatar_url else None,
            description=UserDescription(description),
            created_at=UserCreatedAt(created_at),
            updated_at=UserUpdatedAt(updated_at)
        )

    def __str__(self) -> str:
        return f"User(id={self.id}, name={self.name})"
 