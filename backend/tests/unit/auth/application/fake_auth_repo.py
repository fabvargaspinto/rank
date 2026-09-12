from core.auth.domain.auth_repo import AuthRepository
from core.auth.domain.auth import Auth
from core.user.domain.user import User

class FakeAuthRepo(AuthRepository):
    def __init__(self):
        self.auths = []
        self.users = []

    def save(self, auth: Auth, user: User):
        self.users.append(user)
        self.auths.append(auth)