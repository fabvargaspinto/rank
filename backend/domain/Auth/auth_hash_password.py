from dataclasses import dataclass
import hashlib
import re

from domain.error.domain_error import InvalidPasswordError

SHA256_HEX_RE = re.compile(r"^[a-f0-9]{64}$")
MIN_PASSWORD_LENGTH = 8
MAX_PASSWORD_LENGTH = 128


@dataclass(frozen=True)
class HashPassword:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", self._validate_hash(self.value))

    @classmethod
    def from_plain(cls, password: str) -> "HashPassword":
        cls._validate_plain(password)
        digest = hashlib.sha256(password.encode()).hexdigest()
        return cls(digest)

    def verify(self, password: str) -> bool:
        return hashlib.sha256(password.encode()).hexdigest() == self.value

    @staticmethod
    def _validate_plain(password: str) -> None:
        if not password or len(password) < MIN_PASSWORD_LENGTH:
            raise InvalidPasswordError("Password is too short")
        if len(password) > MAX_PASSWORD_LENGTH:
            raise InvalidPasswordError("Password is too long")
        if any(char.isspace() for char in password):
            raise InvalidPasswordError("Password cannot contain spaces")
        if not any(char.isupper() for char in password):
            raise InvalidPasswordError("Password must contain at least one uppercase letter")
        if not any(char.islower() for char in password):
            raise InvalidPasswordError("Password must contain at least one lowercase letter")
        if not any(char.isdigit() for char in password):
            raise InvalidPasswordError("Password must contain at least one number")


    @staticmethod
    def _validate_hash(value: str) -> str:
        if not value:
            raise InvalidPasswordError("Password hash is required")
        if not SHA256_HEX_RE.match(value):
            raise InvalidPasswordError("Invalid password hash")
        return value

    def __str__(self) -> str:
        return "********"
