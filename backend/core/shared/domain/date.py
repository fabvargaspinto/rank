from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from core.shared.domain.domain_error import InvalidDateError

@dataclass(frozen=True)
class Date:
    value: datetime

    def __init__(self, value: datetime):
        if not self.validate(value):
            raise InvalidDateError(f"Invalid date: {value}")
        object.__setattr__(self, "value", value)
    
    @classmethod
    def now(cls) -> Date:
        return cls(datetime.now())
    
    @classmethod
    def validate(cls, value: datetime) -> bool:
        return isinstance(value, datetime)

    def to_isoformat(self) -> str:
        return self.value.isoformat()

    @classmethod
    def from_isoformat(cls, value: str | datetime) -> Date:
        if isinstance(value, datetime):
            return cls(value)
        return cls(datetime.fromisoformat(value.replace("Z", "+00:00")))