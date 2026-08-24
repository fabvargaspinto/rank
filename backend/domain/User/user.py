from dataclasses import dataclass

from domain.User.user_avatar_url import UserAvatarUrl
from domain.User.user_created_at import UserCreatedAt
from domain.User.user_description import UserDescription
from domain.User.user_id import UserId
from domain.User.user_name import UserName
from domain.User.user_updated_at import UserUpdatedAt


@dataclass(frozen=True)
class User:
    id: UserId
    name: UserName
    avatar_url: UserAvatarUrl
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

    def __str__(self) -> str:
        return f"User(id={self.id}, name={self.name})"
