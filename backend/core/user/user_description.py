from core.share.domain.string import String
from core.user.user_error import InvalidUserDescriptionError

MAX_DESCRIPTION_LENGTH = 1024


class UserDescription(String):
    @classmethod
    def validate(cls, value: str) -> str:
        if len(value) > MAX_DESCRIPTION_LENGTH:
            raise InvalidUserDescriptionError("Description is too long")
        return value
