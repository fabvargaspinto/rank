import re
from dataclasses import dataclass
from typing import NoReturn

from core.auth.domain.auth_error import InvalidEmailError
from core.shared.domain.string import String

_EMAIL = re.compile(r"^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$")


@dataclass(frozen=True)
class AuthEmail(String):
    def _reject_type(self) -> NoReturn:
        raise InvalidEmailError("El email no es válido")

    def normalize(self, value: str) -> str:
        return value.strip().lower()

    def validate(self, value: str) -> None:
        if _EMAIL.fullmatch(value) is None:
            raise InvalidEmailError("El email no es válido")
