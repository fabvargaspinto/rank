from dataclasses import dataclass

from core.user.domain.user_avatar import UserAvatar
from core.user.domain.user_created_at import UserCreatedAt
from core.user.domain.user_description import UserDescription
from core.user.domain.user_id import UserId
from core.user.domain.user_name import UserName
from core.user.domain.user_updated_at import UserUpdatedAt


@dataclass
class User:
    id: UserId
    name: UserName | None
    avatar: UserAvatar | None
    description: UserDescription | None
    created_at: UserCreatedAt
    updated_at: UserUpdatedAt

    @staticmethod
    def create_empty() -> "User":
        return User(
            id=UserId.generate(),
            name=None,
            avatar=None,
            description=None,
            created_at=UserCreatedAt.now(),
            updated_at=UserUpdatedAt.now(),
        )

    def has_name(self) -> bool:
        return self.name is not None and self.name.value != ""

    def update_profile(
        self,
        name: str,
        avatar: str | None = None,
        description: str | None = None,
    ) -> None:
        self.name = UserName(name)

        avatar_value = avatar.strip() if avatar else ""
        self.avatar = UserAvatar(avatar_value) if avatar_value else None

        if description is None or not description.strip():
            self.description = None
        else:
            self.description = UserDescription(description)

        self.updated_at = UserUpdatedAt.now()
