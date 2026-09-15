from dataclasses import dataclass

from core.shared.domain.date import Date


@dataclass(frozen=True)
class UserCreatedAt(Date):
    pass
