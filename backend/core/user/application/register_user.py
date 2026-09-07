from core.user.domain.user import User
from core.user.domain.user_id import UserId
from core.user.domain.user_name import UserName


class RegisterUser:
    def register(self, name: str) -> User:
        return User.create(
            name=UserName(name),
            avatar_url=None,
            description=None,
        )
