from core.user.domain.user import User


def test_create_empty_user_has_generated_id() -> None:
    user = User.create_empty()

    assert user.id.value
    assert user.name is None
    assert user.avatar is None
    assert user.description is None


def test_to_primitive_roundtrip() -> None:
    user = User.create_empty()
    restored = User.from_primitive(user.to_primitive())

    assert restored.id.value == user.id.value
    assert restored.name is None
    assert restored.avatar is None
    assert restored.description is None
