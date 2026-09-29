from dataclasses import dataclass
from typing import Any

from core.user.application.application_error import UserNotFoundError
from core.user.domain.user import User
from core.user.domain.user_error import (
    UsernameAlreadyTakenError,
    UserProfileNotFoundError,
)
from core.user.domain.user_repo import UserRepository

UNSET: Any = object()


@dataclass(frozen=True)
class UpdateProfileCommand:
    name: str
    display_name: str | None | object = UNSET
    avatar: str | None | object = UNSET
    description: str | None = None
    links: list[str] | None = None


class UpdateUser:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def execute(self, auth_id: str, command: UpdateProfileCommand) -> User:
        user = self.user_repo.get_user_by_auth_id(auth_id)
        if user is None:
            raise UserNotFoundError("El usuario no existe")

        user.rename(command.name)
        self._apply_display_name(user, command.display_name)
        self._apply_avatar(user, command.avatar)
        user.describe(command.description)

        if user.name is None:
            raise UserNotFoundError("El usuario no existe")

        if command.links is not None:
            user.replace_links(command.links)

        taken = self.user_repo.get_user_by_name(user.name.value)
        if taken is not None and taken.id != user.id:
            raise UsernameAlreadyTakenError("Ese nombre ya está en uso")

        self._save(user)
        return user

    def _save(self, user: User) -> None:
        try:
            self.user_repo.save(user)
        except UserProfileNotFoundError as exc:
            raise UserNotFoundError("El usuario no existe") from exc

    def _apply_display_name(
        self,
        user: User,
        display_name: str | None | object,
    ) -> None:
        if display_name is UNSET:
            return
        if not isinstance(display_name, str) or not display_name.strip():
            user.clear_display_name()
            return
        user.change_display_name(display_name)

    def _apply_avatar(self, user: User, avatar: str | None | object) -> None:
        if avatar is UNSET:
            return
        if not isinstance(avatar, str) or not avatar.strip():
            user.remove_avatar()
            return
        user.change_avatar(avatar)
