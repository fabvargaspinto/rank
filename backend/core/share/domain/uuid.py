from uuid6 import uuid7

from core.share.domain.domain_error import InvalidUUIDError


class UUID:
    value: str

    def __init__(self, value: str) -> None:
        if not self.validate(value):
            raise InvalidUUIDError("Invalid UUID")
        self.value = value

    @classmethod
    def generate(cls) -> "UUID":
        generated = uuid7()
        return cls(str(generated))

    @classmethod
    def validate(cls, value: str) -> bool:
        try:
            uuid7(value)
            return True
        except (ValueError, TypeError, AttributeError):
            return False

    def __str__(self) -> str:
        return self.value
