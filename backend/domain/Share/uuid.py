import uuid

from domain.error.domain_error import InvalidUUIDError


class UUID:
    value: str

    def __init__(self, value: str) -> None:
        if not self.validate(value):
            raise InvalidUUIDError("Invalid UUID")
        self.value = value

    @classmethod
    def generate(cls) -> "UUID":
        return cls(str(uuid.uuid7()))

    @classmethod
    def validate(cls, value: str) -> bool:
        try:
            uuid.UUID(value)
            return True
        except (ValueError, TypeError, AttributeError):
            return False

    def __str__(self) -> str:
        return self.value
