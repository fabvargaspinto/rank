import pytest

from core.user.application.application_error import UserNotFoundError
from core.user.application.get_user_by_name import GetUserByName
from core.user.domain.user import User
from core.user.domain.user_name import UserName
from tests.unit.user.application.fake_user_repo import FakeUserRepo

USERNAME = "luna"


def _named_user() -> User:
    user = User.create_empty()
    user.name = UserName(USERNAME)
    return user


class TestGetUserByName:
    def setup_method(self):
        self.repo = FakeUserRepo()
        self.use_case = GetUserByName(self.repo)

    def test_returns_user_by_name(self):
        user = _named_user()
        self.repo.users_by_name[USERNAME] = user

        result = self.use_case.execute(f"  {USERNAME}  ")

        assert result is user

    def test_raises_when_name_is_unknown(self):
        with pytest.raises(UserNotFoundError, match="El usuario no existe"):
            self.use_case.execute(USERNAME)

    def test_raises_when_name_is_blank(self):
        with pytest.raises(UserNotFoundError, match="El usuario no existe"):
            self.use_case.execute("   ")
