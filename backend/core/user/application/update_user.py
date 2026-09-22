from core.user.application.application_error import (
    UserNameAlreadyExistsError,
    UserNotFoundError,
)
from core.user.domain.user import UNSET, User
from core.user.domain.user_repo import UserRepository


class UpdateUser:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def execute(
        self,
        auth_id: str,
        name: str,
        avatar: str | None | object = UNSET,
        description: str | None = None,
        links: list[str] | None = None,
    ) -> User:
        user = self.user_repo.get_user_by_auth_id(auth_id)
        if user is None:
            raise UserNotFoundError("El usuario no existe")

        user.update_profile(name=name, avatar=avatar, description=description)
        if user.name is None:
            raise UserNotFoundError("El usuario no existe")

        if links is not None:
            user.replace_links(links)

        taken = self.user_repo.get_user_by_name(user.name.value)
        if taken is not None and taken.id != user.id:
            raise UserNameAlreadyExistsError("Ese nombre ya está en uso")

        updated = self.user_repo.update_user(user)
        if updated is None:
            raise UserNotFoundError("El usuario no existe")
        return updated
