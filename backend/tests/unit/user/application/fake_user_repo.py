from core.user.domain.user import User
from core.user.domain.user_repo import UserRepository


class FakeUserRepo(UserRepository):
    def __init__(self) -> None:
        self.users_by_id: dict[str, User] = {}
        self.users_by_auth_id: dict[str, User] = {}
        self.users_by_name: dict[str, User] = {}

    def get_user(self, user_id: str) -> User | None:
        return self.users_by_id.get(user_id)

    def get_user_by_auth_id(self, auth_id: str) -> User | None:
        return self.users_by_auth_id.get(auth_id)

    def get_user_by_name(self, name: str) -> User | None:
        return self.users_by_name.get(name)

    def update_user(self, user: User) -> User | None:
        auth_id = next(
            (
                key
                for key, stored in self.users_by_auth_id.items()
                if stored.id == user.id
            ),
            None,
        )
        if user.id.value not in self.users_by_id and auth_id is None:
            return None

        for name, stored in list(self.users_by_name.items()):
            if stored.id == user.id:
                del self.users_by_name[name]

        self.users_by_id[user.id.value] = user
        if auth_id is not None:
            self.users_by_auth_id[auth_id] = user
        if user.name is not None:
            self.users_by_name[user.name.value] = user
        return user
