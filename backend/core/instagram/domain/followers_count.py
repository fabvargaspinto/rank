from dataclasses import dataclass

from core.instagram.domain.errors import InvalidFollowersCountError


@dataclass(frozen=True)
class FollowersCount:
    value: int

    def __post_init__(self) -> None:
        if isinstance(self.value, bool) or not isinstance(self.value, int):
            raise InvalidFollowersCountError(
                "La cantidad de followers tiene que ser un número"
            )
        if self.value < 0:
            raise InvalidFollowersCountError(
                "La cantidad de followers no puede ser negativa"
            )
