import pytest

from core.user.application.application_error import (
    UserNameAlreadyExistsError,
    UserNotFoundError,
)
from core.user.application.update_user import UpdateUser
from core.user.domain.user import User
from core.user.domain.user_error import InvalidUserNameError
from core.user.domain.user_name import UserName
from tests.unit.user.application.fake_user_repo import FakeUserRepo

AUTH_ID = "660e8400-e29b-41d4-a716-446655440000"
OTHER_AUTH_ID = "770e8400-e29b-41d4-a716-446655440000"


class TestUpdateUser:
    def setup_method(self):
        self.repo = FakeUserRepo()
        self.use_case = UpdateUser(self.repo)

    def test_updates_profile_for_current_user(self):
        user = User.create_empty()
        self.repo.users_by_auth_id[AUTH_ID] = user

        result = self.use_case.execute(
            AUTH_ID,
            name="luna",
            avatar="https://example.com/avatar.jpg",
            description="Cantautora",
        )

        assert result.name is not None
        assert result.name.value == "luna"
        assert result.avatar is not None
        assert result.avatar.value == "https://example.com/avatar.jpg"
        assert result.description is not None
        assert result.description.value == "Cantautora"
        assert self.repo.users_by_name["luna"] is result

    def test_keeps_name_when_updating_own_profile(self):
        user = User.create_empty()
        user.name = UserName("luna")
        self.repo.users_by_auth_id[AUTH_ID] = user
        self.repo.users_by_name["luna"] = user

        result = self.use_case.execute(
            AUTH_ID,
            name="luna",
            description="Cantautora",
        )

        assert result.name is not None
        assert result.name.value == "luna"
        assert result.description is not None
        assert result.description.value == "Cantautora"

    def test_raises_when_auth_id_is_unknown(self):
        with pytest.raises(UserNotFoundError, match="El usuario no existe"):
            self.use_case.execute(AUTH_ID, name="luna")

    def test_raises_when_name_is_taken(self):
        user = User.create_empty()
        taken = User.create_empty()
        taken.name = UserName("luna")
        self.repo.users_by_auth_id[AUTH_ID] = user
        self.repo.users_by_auth_id[OTHER_AUTH_ID] = taken
        self.repo.users_by_name["luna"] = taken

        with pytest.raises(UserNameAlreadyExistsError, match="Ese nombre ya está en uso"):
            self.use_case.execute(AUTH_ID, name="luna")

    def test_raises_when_name_is_invalid(self):
        user = User.create_empty()
        self.repo.users_by_auth_id[AUTH_ID] = user

        with pytest.raises(InvalidUserNameError):
            self.use_case.execute(AUTH_ID, name="   ")
