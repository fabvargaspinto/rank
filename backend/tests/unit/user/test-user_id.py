from core.user.domain.user_id import UserId


class TestUserId:

    def test_should_create_user_id(self):
        value = "550e8400-e29b-41d4-a716-446655440000"

        user_id = UserId(value)

        assert user_id.value == value

    def test_should_generate_user_id(self):
        user_id = UserId.generate()

        assert user_id is not None
        assert user_id.value is not None

    def test_should_generate_different_ids(self):
        first_id = UserId.generate()
        second_id = UserId.generate()

        assert first_id != second_id