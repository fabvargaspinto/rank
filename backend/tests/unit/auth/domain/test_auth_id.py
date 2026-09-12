from core.auth.domain.auth_id import AuthId


class TestAuthId:

    def test_should_create_auth_id(self):
        value = "550e8400-e29b-41d4-a716-446655440000"

        auth_id = AuthId(value)

        assert auth_id.value == value

    def test_should_generate_auth_id(self):
        auth_id = AuthId.generate()

        assert auth_id is not None
        assert auth_id.value is not None

    def test_should_generate_different_ids(self):
        first_id = AuthId.generate()
        second_id = AuthId.generate()

        assert first_id != second_id