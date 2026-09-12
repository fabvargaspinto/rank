from typing import Protocol

from core.user.domain.user import User
from core.user.domain.user_id import UserId


class UserRepository(Protocol):
    def save(self, user: User) -> None:
        pass

    def find_by_id(self, id: UserId) -> User | None:
        pass