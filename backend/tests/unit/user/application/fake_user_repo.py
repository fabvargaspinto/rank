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
