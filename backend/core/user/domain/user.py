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
