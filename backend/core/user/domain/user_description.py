from dataclasses import dataclass

from core.shared.domain.string import String
from core.user.domain.user_error import InvalidUserDescriptionError


@dataclass(frozen=True)
class UserDescription(String):
    MAX_LENGTH = 250

    def validate(self, value: str) -> None:
        if len(value) > self.MAX_LENGTH:
            raise InvalidUserDescriptionError(
                f"La descripción debe tener menos de {self.MAX_LENGTH} caracteres"
            )
