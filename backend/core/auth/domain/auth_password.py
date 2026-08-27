from core.share.domain.string import String
from core.auth.domain.auth_error import InvalidPasswordError
import re

MIN_PASSWORD_LENGTH = 6
MAX_PASSWORD_LENGTH = 72


class AuthPassword(String):
    @classmethod
    def validate(cls, value: str) -> str:
        if not value:
            raise InvalidPasswordError("Password is required")
        if len(value) < MIN_PASSWORD_LENGTH:
            raise InvalidPasswordError("Password is too short")
        if len(value) > MAX_PASSWORD_LENGTH:
            raise InvalidPasswordError("Password is too long")
        if not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$', value):
            raise InvalidPasswordError("Password must contain at least one uppercase letter, one lowercase letter, one number, and one special character")
        return value
