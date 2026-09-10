from typing import Protocol
from core.auth.domain.auth import Auth
from core.user.domain.user import User


class AuthRepository(Protocol):
    
    def create_user(self, user: User, auth: Auth) -> None:
        pass
    