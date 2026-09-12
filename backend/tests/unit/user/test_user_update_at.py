from core.user.domain.user_updated_at import UserUpdatedAt

# TODO: hacer un clock mock para testear el updated_at

class TestUserUpdatedAt:

    def test_should_create_current_date(self):
        updated_at = UserUpdatedAt.now()

        assert updated_at is not None

    def test_should_create_date_from_isoformat(self):
        value = "2026-09-12T12:00:00"

        updated_at = UserUpdatedAt.from_isoformat(value)

        assert updated_at.to_isoformat() == value