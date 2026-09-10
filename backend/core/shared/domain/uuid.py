from __future__ import annotations

from dataclasses import dataclass
from uuid6 import uuid7
from core.shared.domain.domain_error import InvalidUUIDError

@dataclass(frozen=True)
class UUID:
    value: str

    def __init__(self, value: str):
        if not self.validate(value):
            raise InvalidUUIDError(f"Invalid UUID: {value}")
        object.__setattr__(self, "value", value)

    @classmethod
    def generate(cls) -> UUID:
        return cls(str(uuid7()))
    
    @classmethod
    def validate(cls, value: str) -> bool:
        try:
            uuid7(value)
            return True
        except ValueError:
            return False
        
    @classmethod
    def from_string(cls, value: str) -> UUID:
        return cls(value)