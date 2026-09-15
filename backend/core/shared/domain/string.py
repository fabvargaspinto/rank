from dataclasses import dataclass

from core.shared.domain.domain_error import InvalidStringError


@dataclass
class String:
    value: str

    def __post_init__(self) -> None:
        self.validate()

    def validate(self) -> None:
        if not isinstance(self.value, str):
            raise InvalidStringError("Invalid string")
        self.value = self.value.strip()
