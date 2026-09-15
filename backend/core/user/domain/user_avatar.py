from dataclasses import dataclass

from core.shared.domain.string import String
from core.user.domain.user_error import InvalidUserAvatarError


@dataclass
class UserAvatar(String):
    value: str


    def __post_init__(self) -> None:
        self.validate()

    def validate(self) -> None:
        self.value = self.value.strip()

        if not self.value.startswith("https://"):
            raise InvalidUserAvatarError("El avatar debe ser una URL válida")
