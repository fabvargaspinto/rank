from core.user.application.application_error import UserNotFoundError
from core.user.domain.user import User
from core.user.domain.user_repo import UserRepository


class GetUserByName:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def execute(self, name: str) -> User:
        username = name.strip()
        if not username:
            raise UserNotFoundError("El usuario no existe")

        user = self.user_repo.get_user_by_name(username)
        if user is None:
            raise UserNotFoundError("El usuario no existe")
        return user
