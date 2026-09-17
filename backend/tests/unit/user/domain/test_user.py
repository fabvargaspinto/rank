from core.user.domain.user import User
from core.user.domain.user_avatar import UserAvatar
from core.user.domain.user_description import UserDescription
from core.user.domain.user_name import UserName

USER_ID = "550e8400-e29b-41d4-a716-446655440000"


def create_user_with_values():
    empty_user = User.create_empty()

    return User(
        id=empty_user.id,
        name=UserName("John Doe"),
        avatar=UserAvatar("https://example.com/avatar.jpg"),
        description=UserDescription("My description"),
        created_at=empty_user.created_at,
        updated_at=empty_user.updated_at,
    )

class TestUser:

    def test_should_create_empty_user(self):
        user = User.create_empty()

        assert user.id is not None
        assert user.name is None
        assert user.avatar is None
        assert user.description is None
        assert user.created_at is not None
        assert user.updated_at is not None

    def test_should_create_user_with_values(self):
        user = create_user_with_values()

        assert user.name.value == "John Doe"
        assert user.avatar.value == "https://example.com/avatar.jpg"
        assert user.description.value == "My description"

    def test_has_name_is_false_for_empty_user(self):
        user = User.create_empty()

        assert user.has_name() is False

    def test_has_name_is_true_when_name_is_set(self):
        user = create_user_with_values()

        assert user.has_name() is True
