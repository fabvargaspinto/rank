from dataclasses import dataclass

from core.instagram.domain.errors import InvalidInstagramUsernameError


@dataclass(frozen=True)
class InstagramUsername:
    value: str

    def __post_init__(self) -> None:
        if not isinstance(self.value, str):
            raise InvalidInstagramUsernameError("El usuario de Instagram no es válido")

        normalized = self.value.strip().lstrip("@")
        if not normalized or len(normalized) > 64:
            raise InvalidInstagramUsernameError("El usuario de Instagram no es válido")

        object.__setattr__(self, "value", normalized)
