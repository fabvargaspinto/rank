from datetime import UTC, datetime

from core.user.domain.user import User
from core.user.domain.user_avatar import UserAvatar
from core.user.domain.user_created_at import UserCreatedAt
from core.user.domain.user_description import UserDescription
from core.user.domain.user_id import UserId
from core.user.domain.user_name import UserName
from core.user.domain.user_updated_at import UserUpdatedAt
from core.user.infrastructure.user_mapper import UserMapper

USER_ID = "550e8400-e29b-41d4-a716-446655440000"
CREATED_AT = datetime(2026, 1, 2, 3, 4, 5, tzinfo=UTC)
UPDATED_AT = datetime(2026, 1, 3, 4, 5, 6, tzinfo=UTC)


def _mapper() -> UserMapper:
    return UserMapper()


def _full_user() -> User:
    return User(
        id=UserId(USER_ID),
        name=UserName("Luna Reyes"),
        avatar=UserAvatar("https://example.com/avatar.jpg"),
        description=UserDescription("Cantautora"),
        created_at=UserCreatedAt(CREATED_AT),
        updated_at=UserUpdatedAt(UPDATED_AT),
    )


class TestUserMapper:
    def test_to_row_uses_public_users_columns(self):
        user = _full_user()

        row = _mapper().to_row(user)

        assert row == {
            "id": USER_ID,
            "name": "Luna Reyes",
            "avatar_url": "https://example.com/avatar.jpg",
            "description": "Cantautora",
            "created_at": user.created_at.to_isoformat(),
            "updated_at": user.updated_at.to_isoformat(),
        }

    def test_to_row_keeps_optional_fields_null_for_empty_user(self):
        user = User.create_empty()

        row = _mapper().to_row(user)

        assert row["id"] == user.id.value
        assert row["name"] is None
        assert row["avatar_url"] is None
        assert row["description"] is None

    def test_to_domain_rebuilds_user_from_row(self):
        mapper = _mapper()
        user = _full_user()

        restored = mapper.to_domain(mapper.to_row(user))

        assert restored == user

    def test_to_domain_accepts_empty_optional_fields(self):
        user = User.create_empty()
        row = {
            "id": user.id.value,
            "name": None,
            "avatar_url": None,
            "description": None,
            "created_at": user.created_at.to_isoformat(),
            "updated_at": user.updated_at.to_isoformat(),
        }

        restored = _mapper().to_domain(row)

        assert restored.id == user.id
        assert restored.name is None
        assert restored.avatar is None
        assert restored.description is None
