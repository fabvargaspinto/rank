from core.user.domain.user import User
from core.user.domain.user_avatar import UserAvatar
from core.user.domain.user_created_at import UserCreatedAt
from core.user.domain.user_description import UserDescription
from core.user.domain.user_id import UserId
from core.user.domain.user_name import UserName
from core.user.domain.user_updated_at import UserUpdatedAt


class UserMapper:
    def to_domain(self, row: dict) -> User:
        return User(
            id=UserId(row["id"]),
            name=self._optional_name(row.get("name")),
            avatar=self._optional_avatar(row.get("avatar_url")),
            description=self._optional_description(row.get("description")),
            links=[],
            created_at=UserCreatedAt.from_isoformat(row["created_at"]),
            updated_at=UserUpdatedAt.from_isoformat(row["updated_at"]),
        )

    def to_row(self, user: User) -> dict:
        return {
            "id": user.id.value,
            "name": user.name.value if user.name else None,
            "avatar_url": user.avatar.value if user.avatar else None,
            "description": user.description.value if user.description else None,
            "created_at": user.created_at.to_isoformat(),
            "updated_at": user.updated_at.to_isoformat(),
        }

    def _optional_name(self, value: object) -> UserName | None:
        if not isinstance(value, str) or not value.strip():
            return None
        return UserName(value)

    def _optional_avatar(self, value: object) -> UserAvatar | None:
        if not isinstance(value, str) or not value.strip():
            return None
        return UserAvatar(value)

    def _optional_description(self, value: object) -> UserDescription | None:
        if not isinstance(value, str):
            return None
        return UserDescription(value)
