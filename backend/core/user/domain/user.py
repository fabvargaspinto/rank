from dataclasses import dataclass

from core.user.domain.user_id import UserId
from core.user.domain.user_name import UserName
from core.user.domain.user_avatar import UserAvatar
from core.user.domain.user_description import UserDescription
from core.user.domain.user_created_at import UserCreatedAt
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

    def to_primitive(self) -> dict:
        return {
            "id": self.id.value,
            "name": self.name.value if self.name else None,
            "avatar": self.avatar.value if self.avatar else None,
            "description": self.description.value if self.description else None,
            "created_at": self.created_at.value,
            "updated_at": self.updated_at.value,
        }

    @staticmethod
    def from_primitive(primitive: dict) -> "User":
        return User(
            id=UserId(primitive["id"]),
            name=UserName(primitive["name"]) if primitive["name"] else None,
            avatar=UserAvatar(primitive["avatar"]) if primitive["avatar"] else None,
            description=UserDescription(primitive["description"]) if primitive["description"] else None,
            created_at=UserCreatedAt(primitive["created_at"]),
            updated_at=UserUpdatedAt(primitive["updated_at"]),
        )
        