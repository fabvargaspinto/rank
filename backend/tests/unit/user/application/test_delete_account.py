from core.user.application.delete_account import DeleteAccount
from core.user.domain.user import User
from tests.unit.auth.application.fake_auth_repo import FakeAuthRepo
from tests.unit.user.application.fake_avatar_storage import FakeAvatarStorage
from tests.unit.user.application.fake_user_repo import FakeUserRepo

AUTH_ID = "660e8400-e29b-41d4-a716-446655440000"


class TestDeleteAccount:
    def setup_method(self):
        self.users = FakeUserRepo()
        self.avatars = FakeAvatarStorage()
        self.auth = FakeAuthRepo()
        self.use_case = DeleteAccount(self.users, self.avatars, self.auth)

    def test_deletes_profile_avatar_and_identity(self):
        user = User.create_empty()
        self.users.users_by_id[user.id.value] = user
        self.users.users_by_auth_id[AUTH_ID] = user

        self.use_case.execute(AUTH_ID)

        assert user.id.value not in self.users.users_by_id
        assert AUTH_ID not in self.users.users_by_auth_id
        assert self.avatars.deleted == []
        assert self.auth.deleted_ids == [AUTH_ID]

    def test_deletes_the_stored_avatar(self):
        user = User.create_empty()
        path = f"{user.id.value}/550e8400-e29b-41d4-a716-446655440000.webp"
        user.change_avatar(path)
        self.users.users_by_id[user.id.value] = user
        self.users.users_by_auth_id[AUTH_ID] = user

        self.use_case.execute(AUTH_ID)

        assert self.avatars.deleted == [path]

    def test_does_not_delete_another_users_avatar_object(self):
        from core.user.domain.user_avatar import UserAvatar

        user = User.create_empty()
        foreign = (
            "550e8400-e29b-41d4-a716-446655440099/"
            "660e8400-e29b-41d4-a716-446655440000.webp"
        )
        user.avatar = UserAvatar(foreign)
        self.users.users_by_id[user.id.value] = user
        self.users.users_by_auth_id[AUTH_ID] = user

        self.use_case.execute(AUTH_ID)

        assert self.avatars.deleted == []

    def test_deletes_identity_when_profile_is_missing(self):
        self.use_case.execute(AUTH_ID)

        assert self.avatars.deleted == []
        assert self.auth.deleted_ids == [AUTH_ID]
