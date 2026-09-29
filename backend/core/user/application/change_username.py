from core.user.domain.user import User
from core.user.domain.user_error import UsernameAlreadyTakenError
from core.user.domain.user_repo import UserRepository


class ChangeUsername:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def execute(self, user: User, name: str) -> None:
        user.rename(name)
        taken = self.user_repo.get_user_by_name(user.name.value)
        if taken is not None and taken.id != user.id:
            raise UsernameAlreadyTakenError("Ese nombre ya está en uso")
