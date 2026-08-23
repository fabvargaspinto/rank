from dataclasses import dataclass
import re

from domain.error.domain_error import InvalidEmailError

EMAIL_RE = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")


@dataclass(frozen=True)
class Email:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", self._validate(self.value))

    @staticmethod
    def _validate(value: str) -> str:
        if not value or not value.strip():
            raise InvalidEmailError("Email is required")

        email = value.strip().lower()

        if len(email) < 3:
            raise InvalidEmailError("Email is too short")
        if len(email) > 255:
            raise InvalidEmailError("Email is too long")
        if not EMAIL_RE.match(email):
            raise InvalidEmailError("Invalid email")

        return email

    def __str__(self) -> str:
        return self.value
