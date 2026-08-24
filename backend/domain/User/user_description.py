from domain.Share.string import String
from domain.error.domain_error import InvalidDescriptionError

MAX_DESCRIPTION_LENGTH = 1024


class UserDescription(String):
    @classmethod
    def validate(cls, value: str) -> str:
        if len(value) > MAX_DESCRIPTION_LENGTH:
            raise InvalidDescriptionError("Description is too long")
        return value
