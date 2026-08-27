from core.share.domain.string import String
from core.auth.domain.auth_error import InvalidPasswordError

MIN_PASSWORD_LENGTH = 6
MAX_PASSWORD_LENGTH = 72


class Password(String):
    @classmethod
    def validate(cls, value: str) -> str:
        if not value:
            raise InvalidPasswordError("Password is required")
        if len(value) < MIN_PASSWORD_LENGTH:
            raise InvalidPasswordError("Password is too short")
        if len(value) > MAX_PASSWORD_LENGTH:
            raise InvalidPasswordError("Password is too long")
        return value
