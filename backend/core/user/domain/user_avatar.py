import re
from dataclasses import dataclass

from core.shared.domain.string import String
from core.shared.domain.user_id import UserId
from core.user.domain.user_error import InvalidUserAvatarError

_UUID = (
    r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"
)
_PATH = re.compile(rf"^{_UUID}/{_UUID}\.webp$")


@dataclass(frozen=True)
class UserAvatar(String):
    def validate(self, value: str) -> None:
        if _PATH.fullmatch(value) is None:
            raise InvalidUserAvatarError(
                "El avatar debe ser una imagen del bucket propio"
            )

    def belongs_to(self, user_id: UserId) -> bool:
        folder = self.value.split("/", 1)[0]
        return folder.lower() == user_id.value.lower()
