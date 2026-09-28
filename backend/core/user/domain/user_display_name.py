from dataclasses import dataclass

from core.shared.domain.string import String
from core.user.domain.user_error import InvalidUserDisplayNameError


@dataclass(frozen=True)
class UserDisplayName(String):
    MIN_LENGTH = 1
    MAX_LENGTH = 50

    def validate(self, value: str) -> None:
        if len(value) < self.MIN_LENGTH or len(value) > self.MAX_LENGTH:
            raise InvalidUserDisplayNameError(
                f"El nombre debe tener entre {self.MIN_LENGTH} "
                f"y {self.MAX_LENGTH} caracteres"
            )
