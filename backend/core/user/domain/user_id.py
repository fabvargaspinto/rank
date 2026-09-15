from dataclasses import dataclass

from core.shared.domain.uuid import UUID


@dataclass(frozen=True)
class UserId(UUID):
    pass
