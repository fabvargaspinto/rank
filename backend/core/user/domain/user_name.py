import re
from dataclasses import dataclass
from typing import ClassVar

from core.user.domain.user_error import InvalidUserNameError


@dataclass(frozen=True)
class UserName:
    value: str

    PATTERN: ClassVar[re.Pattern[str]] = re.compile(
        r"^[a-z0-9][a-z0-9._-]{1,28}[a-z0-9]$"
    )
    RESERVED: ClassVar[frozenset[str]] = frozenset(
        {
            "admin",
            "api",
            "assets",
            "auth",
            "ayuda",
            "contacto",
            "dashboard",
            "favicon.ico",
            "first",
            "forgot-password",
            "icon",
            "instagram",
            "legal",
            "login",
            "opengraph-image",
            "privacy",
            "privacidad",
            "register",
            "reset-password",
            "robots.txt",
            "settings",
            "sitemap.xml",
            "soporte",
            "static",
            "terms",
            "terminos",
            "www",
        }
    )
    MESSAGE: ClassVar[str] = (
        "Usá entre 3 y 30 letras minúsculas, números, puntos, "
        "guiones o guiones bajos"
    )

    def __post_init__(self) -> None:
        if not isinstance(self.value, str):
            raise InvalidUserNameError("El usuario es obligatorio")

        normalized = self.value.strip().lower()
        if not self.PATTERN.fullmatch(normalized) or normalized in self.RESERVED:
            raise InvalidUserNameError(self.MESSAGE)

        object.__setattr__(self, "value", normalized)
