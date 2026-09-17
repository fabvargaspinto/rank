from core.user.application.application_error import UserNotFoundError
from core.user.domain.user import User
from core.user.domain.user_repo import UserRepository


class GetUser:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def execute(self, auth_id: str) -> User:
        user = self.user_repo.get_user_by_auth_id(auth_id)
        if user is None:
            raise UserNotFoundError("El usuario no existe")
        return user
