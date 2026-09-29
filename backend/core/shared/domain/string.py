from dataclasses import dataclass
from typing import NoReturn

from core.shared.domain.domain_error import InvalidStringError


@dataclass(frozen=True)
class String:
    value: str

    def __post_init__(self) -> None:
        raw = self.value
        if not isinstance(raw, str):
            self._reject_type()
        normalized = self.normalize(raw)
        self.validate(normalized)
        object.__setattr__(self, "value", normalized)

    def normalize(self, value: str) -> str:
        return value.strip()

    def validate(self, value: str) -> None:
        return

    def _reject_type(self) -> NoReturn:
        raise InvalidStringError("El texto no es válido")
