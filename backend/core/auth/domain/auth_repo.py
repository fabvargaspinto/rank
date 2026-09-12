from typing import Protocol

from core.auth.domain.auth import Auth
from core.user.domain.user import User

class AuthRepository(Protocol):
   
   def save(self, auth: Auth, user: User) -> None:
      pass

   def find_by_email(self, email: str) -> Auth | None:
      pass