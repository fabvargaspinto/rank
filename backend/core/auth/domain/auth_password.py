import re
from dataclasses import dataclass

from core.auth.domain.auth_error import InvalidAuthPasswordError
from core.shared.domain.string import String


@dataclass
class AuthPassword(String):
    value: str
    MIN_LENGTH = 8
    MAX_LENGTH = 64
    HAS_LETTER = re.compile(r"[^\W\d_]")
    HAS_DIGIT = re.compile(r"\d")
    HAS_SPACE = re.compile(r"\s")

    def __post_init__(self) -> None:
        self.validate()

    def validate(self) -> None:
        self._validate_min_length()
        self._validate_max_length()
        self._validate_no_spaces()
        self._validate_has_letter()
        self._validate_has_digit()

    def _validate_min_length(self) -> None:
        if len(self.value) < self.MIN_LENGTH:
            raise InvalidAuthPasswordError(
                f"La contraseña debe tener al menos {self.MIN_LENGTH} caracteres"
            )

    def _validate_max_length(self) -> None:
        if len(self.value) > self.MAX_LENGTH:
            raise InvalidAuthPasswordError(
                f"La contraseña debe tener menos de {self.MAX_LENGTH} caracteres"
            )

    def _validate_no_spaces(self) -> None:
        if self.HAS_SPACE.search(self.value):
            raise InvalidAuthPasswordError("La contraseña no debe tener espacios")

    def _validate_has_letter(self) -> None:
        if not self.HAS_LETTER.search(self.value):
            raise InvalidAuthPasswordError("La contraseña debe incluir al menos una letra")

    def _validate_has_digit(self) -> None:
        if not self.HAS_DIGIT.search(self.value):
            raise InvalidAuthPasswordError("La contraseña debe incluir al menos un número")
