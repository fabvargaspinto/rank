from datetime import datetime

from domain.error.domain_error import InvalidDateError


class Date:
    value: datetime

    def __init__(self, value: datetime) -> None:
        if not isinstance(value, datetime):
            raise InvalidDateError("Date must be a datetime")
        self.value = value

    @classmethod
    def generate(cls) -> "Date":
        return cls(datetime.now())

    def __str__(self) -> str:
        return self.value.isoformat()
