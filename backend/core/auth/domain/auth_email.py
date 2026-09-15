import re
from dataclasses import dataclass

from core.auth.domain.auth_error import InvalidEmailError
from core.shared.domain.string import String


@dataclass
class AuthEmail(String):
    value: str

    def __post_init__(self) -> None:
        self.validate()

    def validate(self) -> None:
        if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", self.value):
            raise InvalidEmailError("Invalid email address")
        self.value = self.value.strip().lower()

