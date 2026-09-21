from dataclasses import dataclass
from urllib.parse import urlparse

from core.shared.domain.string import String
from core.user.domain.user_error import InvalidUserLinkUrlError


@dataclass
class UserLinkUrl(String):
    value: str
    MAX_LENGTH = 2048

    def __post_init__(self) -> None:
        self.validate()

    def validate(self) -> None:
        self.value = self.value.strip()

        if not self.value:
            raise InvalidUserLinkUrlError("La URL debe ser una URL válida")

        if len(self.value) > self.MAX_LENGTH:
            raise InvalidUserLinkUrlError(
                f"La URL debe tener menos de {self.MAX_LENGTH} caracteres"
            )

        if not self.value.startswith("https://"):
            raise InvalidUserLinkUrlError("La URL debe ser una URL válida")

    def host(self) -> str:
        hostname = urlparse(self.value).hostname
        return (hostname or "").lower()
