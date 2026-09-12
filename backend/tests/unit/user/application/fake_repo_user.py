from core.user.domain.user_repo import UserRepo
from core.user.domain.user import User


class FakeRepoUser(UserRepo):
    def __init__(self):
        self.users = []

    def save(self, user: User):
        self.users.append(user)

   
   