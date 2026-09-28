from dataclasses import dataclass

from core.auth.domain.auth_error import InvalidAuthProviderIdError
from core.shared.domain.string import String


@dataclass(frozen=True)
class AuthProviderId(String):
    def validate(self, value: str) -> None:
        if not value:
            raise InvalidAuthProviderIdError(
                "El identificador del proveedor es obligatorio"
            )
