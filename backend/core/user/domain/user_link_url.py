from dataclasses import dataclass
from urllib.parse import urlsplit

from core.shared.domain.https_url import HttpsUrl, is_https_url
from core.user.domain.user_error import InvalidUserLinkUrlError


@dataclass(frozen=True)
class UserLinkUrl(HttpsUrl):
    MAX_LENGTH = 2048

    def validate(self, value: str) -> None:
        if len(value) > self.MAX_LENGTH:
            raise InvalidUserLinkUrlError(
                f"La URL debe tener menos de {self.MAX_LENGTH} caracteres"
            )
        if not is_https_url(value):
            raise InvalidUserLinkUrlError("La URL debe ser una URL válida")

    def host(self) -> str:
        hostname = urlsplit(self.value).hostname
        return (hostname or "").lower()
