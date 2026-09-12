from core.user.domain.user_created_at import UserCreatedAt

# TODO: hacer un clock mock para testear el created_at

class TestUserCreatedAt:

    def test_should_create_current_date(self):
        created_at = UserCreatedAt.now()

        assert created_at is not None

    def test_should_create_date_from_isoformat(self):
        value = "2026-09-12T12:00:00"

        created_at = UserCreatedAt.from_isoformat(value)

        assert created_at.to_isoformat() == value