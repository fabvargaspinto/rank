from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID as PythonUUID
from uuid6 import uuid7

from core.shared.domain.domain_error import InvalidUUIDError


@dataclass(frozen=True)
class UUID:
    value: str

    def __post_init__(self) -> None:
        if not self.validate(self.value):
            raise InvalidUUIDError(f"Invalid UUID: {self.value}")

    @classmethod
    def generate(cls) -> UUID:
        return cls(str(uuid7()))

    @classmethod
    def validate(cls, value: str) -> bool:
        try:
            PythonUUID(value)
            return True
        except (ValueError, TypeError, AttributeError):
            return False

    @classmethod
    def from_string(cls, value: str) -> UUID:
        return cls(value)