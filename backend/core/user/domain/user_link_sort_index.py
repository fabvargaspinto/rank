from dataclasses import dataclass

from core.user.domain.user_error import InvalidUserLinkSortIndexError


@dataclass
class UserLinkSortIndex:
    value: int
    MIN = 0
    MAX = 5

    def __post_init__(self) -> None:
        self.validate()

    def validate(self) -> None:
        if isinstance(self.value, bool) or not isinstance(self.value, int):
            raise InvalidUserLinkSortIndexError(
                f"El índice debe estar entre {self.MIN} y {self.MAX}"
            )

        if self.value < self.MIN or self.value > self.MAX:
            raise InvalidUserLinkSortIndexError(
                f"El índice debe estar entre {self.MIN} y {self.MAX}"
            )
