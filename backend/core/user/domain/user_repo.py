from typing import Protocol

from core.user.domain.user import User


class UserRepository(Protocol):
    def get_user(self, user_id: str) -> User | None:
        pass

    def get_user_by_auth_id(self, auth_id: str) -> User | None:
        pass

    def get_user_by_name(self, name: str) -> User | None:
        pass
