from dataclasses import dataclass
from datetime import datetime
from core.shared.domain.domain_error import InvalidDateError

@dataclass(frozen=True)
class Date:
    value: datetime

    def __init__(self, value: datetime):
        if not self.validate(value):
            raise InvalidDateError(f"Invalid date: {value}")
        object.__setattr__("value", value)
    
    @classmethod
    def now(cls) -> Date:
        return Date(datetime.now())
    
    @classmethod
    def validate(cls, value: datetime) -> bool:
        return isinstance(value, datetime)