from core.share.domain.string import String
from core.user.domain.user_error import InvalidUserDescriptionError

MAX_DESCRIPTION_LENGTH = 300


class UserDescription(String):
    @classmethod
    def validate(cls, value: str) -> str:
        if len(value) > MAX_DESCRIPTION_LENGTH:
            raise InvalidUserDescriptionError("Description is too long")
        return value
