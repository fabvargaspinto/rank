from dataclasses import dataclass
from typing import Any

from core.user.application.application_error import UserNotFoundError
from core.user.application.change_username import ChangeUsername
from core.user.domain.user import User
from core.user.domain.user_error import UserProfileNotFoundError
from core.user.domain.user_repo import UserRepository

UNSET: Any = object()


@dataclass(frozen=True)
class UpdateProfileCommand:
    name: str
    display_name: str | None | object = UNSET
    description: str | None = None
    links: list[str] | None = None


class UpdateUser:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo
        self.change_username = ChangeUsername(user_repo)

    def execute(self, user: User, command: UpdateProfileCommand) -> User:
        self.change_username.execute(user, command.name)
        self._apply_display_name(user, command.display_name)
        user.describe(command.description)

        if command.links is not None:
            user.replace_links(command.links)

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
