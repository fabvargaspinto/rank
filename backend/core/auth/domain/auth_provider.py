from enum import Enum

from core.auth.domain.auth_error import InvalidAuthProviderError


class AuthProvider(Enum):
    EMAIL = "EMAIL"
    OAUTH = "OAUTH"

    def is_email(self) -> bool:
        return self is AuthProvider.EMAIL

    def is_oauth(self) -> bool:
        return self is AuthProvider.OAUTH

    @classmethod
    def from_string(cls, value: str) -> "AuthProvider":
        normalized = value.strip().upper()
        try:
            return cls(normalized)
        except ValueError:
            allowed = ", ".join(provider.value for provider in cls)
            raise InvalidAuthProviderError(
                f"El proveedor de autenticación debe ser uno de los siguientes: {allowed}"
            )
