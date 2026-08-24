import re

from domain.Share.string import String
from domain.error.domain_error import InvalidUserNameError

MAX_USERNAME_LENGTH = 32
MIN_USERNAME_LENGTH = 3
USERNAME_REGEX = re.compile(r"^[a-zA-Z0-9-_]+$")


class UserName(String):
    @classmethod
    def validate(cls, value: str) -> str:
        username = value.strip()

        if len(username) < MIN_USERNAME_LENGTH:
            raise InvalidUserNameError("Username is too short")
        if len(username) > MAX_USERNAME_LENGTH:
            raise InvalidUserNameError("Username is too long")
        if not USERNAME_REGEX.match(username):
            raise InvalidUserNameError("Username contains invalid characters")

        return username
