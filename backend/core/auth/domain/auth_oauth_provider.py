from enum import Enum

from core.auth.domain.auth_error import InvalidAuthOauthProviderError


class AuthOauthProvider(str, Enum):
    GOOGLE = "GOOGLE"

    @classmethod
    def from_string(cls, value: str) -> "AuthOauthProvider":
        normalized = value.strip().upper()
        try:
            return cls(normalized)
        except ValueError:
            allowed = ", ".join(provider.value for provider in cls)
            raise InvalidAuthOauthProviderError(
                f"El proveedor OAuth debe ser uno de los siguientes: {allowed}"
            )
