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

    def test_should_convert_empty_user_to_primitive(self):
        user = User.create_empty()

        primitive = user.to_primitive()

        assert primitive["id"] == user.id.value
        assert primitive["name"] is None
        assert primitive["avatar"] is None
        assert primitive["description"] is None
        assert primitive["created_at"] == user.created_at.value
        assert primitive["updated_at"] == user.updated_at.value

    def test_should_convert_user_with_values_to_primitive(self):
        user = create_user_with_values()

        primitive = user.to_primitive()

        assert primitive["id"] == user.id.value
        assert primitive["name"] == "John Doe"
        assert primitive["avatar"] == "https://example.com/avatar.jpg"
        assert primitive["description"] == "My description"
    

    def test_should_recreate_empty_user_from_primitive(self):
        user = User.create_empty()

        primitive = user.to_primitive()

        recreated_user = User.from_primitive(primitive)

        assert recreated_user == user

    def test_should_recreate_user_with_values_from_primitive(self):
        user = create_user_with_values()

        primitive = user.to_primitive()

        recreated_user = User.from_primitive(primitive)

        assert recreated_user == user

    def test_should_preserve_user_id_when_recreating(self):
        user = User.create_empty()

        primitive = user.to_primitive()

        recreated_user = User.from_primitive(primitive)

        assert recreated_user.id == user.id

    def test_should_preserve_created_at_when_recreating(self):
        user = User.create_empty()

        primitive = user.to_primitive()

        recreated_user = User.from_primitive(primitive)

        assert recreated_user.created_at == user.created_at

    def test_should_preserve_updated_at_when_recreating(self):
        user = User.create_empty()

        primitive = user.to_primitive()

        recreated_user = User.from_primitive(primitive)

        assert recreated_user.updated_at == user.updated_at