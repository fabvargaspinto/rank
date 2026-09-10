from dataclasses import dataclass

from core.shared.domain.uuid import UUID

@dataclass
class UserId(UUID):
    pass