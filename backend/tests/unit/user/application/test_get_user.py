import pytest

from core.user.application.application_error import UserNotFoundError
from core.user.application.get_user import GetUser
from core.user.domain.user import User
from tests.unit.user.application.fake_user_repo import FakeUserRepo

AUTH_ID = "660e8400-e29b-41d4-a716-446655440000"


class TestGetUser:
    def setup_method(self):
        self.repo = FakeUserRepo()
        self.use_case = GetUser(self.repo)

    def test_returns_user_by_auth_id(self):
        user = User.create_empty()
        self.repo.users_by_auth_id[AUTH_ID] = user

        result = self.use_case.execute(AUTH_ID)

        assert result is user

    def test_raises_when_auth_id_is_unknown(self):
        with pytest.raises(UserNotFoundError, match="El usuario no existe"):
            self.use_case.execute(AUTH_ID)
