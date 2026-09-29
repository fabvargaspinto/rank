from typing import Protocol

from core.user.domain.user import User
from core.user.domain.user_error import (
    UsernameAlreadyTakenError,
    UserProfileNotFoundError,
)

__all__ = [
    "UserProfileNotFoundError",
    "UserRepository",
    "UsernameAlreadyTakenError",
]


class UserRepository(Protocol):
    def get_user(self, user_id: str) -> User | None:
        pass

    def get_user_by_auth_id(self, auth_id: str) -> User | None:
        pass

    def get_user_by_name(self, name: str) -> User | None:
        pass

    def save(self, user: User) -> None:
        """Persist the profile and its links in one operation.

        Raises:
            UsernameAlreadyTakenError: the username is already taken.
            UserProfileNotFoundError: there is no profile row for this user.
        """

    def delete_user(self, user_id: str) -> None:
        pass
