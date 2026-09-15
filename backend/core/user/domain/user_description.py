from dataclasses import dataclass

from core.shared.domain.string import String
from core.user.domain.user_error import InvalidUserDescriptionError


@dataclass
class UserDescription(String):

    value: str

    MAX_LENGTH = 250

    def __post_init__(self) -> None:
        self.validate()

    def validate(self) -> None:
        if len(self.value) > self.MAX_LENGTH:
            raise InvalidUserDescriptionError(f"La descripción debe tener menos de {self.MAX_LENGTH} caracteres")
        self.value = self.value.strip()
