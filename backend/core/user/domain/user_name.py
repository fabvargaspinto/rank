from dataclasses import dataclass

from core.shared.domain.string import String
from core.user.domain.user_error import InvalidUserNameError


@dataclass
class UserName(String):
    value: str
    MIN_LENGTH = 1
    MAX_LENGTH = 50

    def __post_init__(self) -> None:
        self.validate()

    def validate(self) -> None:

        self.value = self.value.strip()

        if len(self.value) < self.MIN_LENGTH or len(self.value) > self.MAX_LENGTH:
            raise InvalidUserNameError(
                f"El nombre debe tener entre "
                f"{self.MIN_LENGTH} y {self.MAX_LENGTH} caracteres"
            )
