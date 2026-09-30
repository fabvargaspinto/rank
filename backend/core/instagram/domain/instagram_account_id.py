from dataclasses import dataclass

from core.instagram.domain.errors import InvalidInstagramAccountIdError


@dataclass(frozen=True)
class InstagramAccountId:
    value: str

    def __post_init__(self) -> None:
        if not isinstance(self.value, str):
            raise InvalidInstagramAccountIdError("El id de Instagram no es válido")

        normalized = self.value.strip()
        if not normalized or len(normalized) > 128:
            raise InvalidInstagramAccountIdError("El id de Instagram no es válido")

        object.__setattr__(self, "value", normalized)
