from dataclasses import dataclass

from core.shared.domain.uuid import UUID


@dataclass(frozen=True)
class UserLinkId(UUID):
    pass
