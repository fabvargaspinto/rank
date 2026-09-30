from dataclasses import dataclass

from core.shared.domain.uuid import UUID


@dataclass(frozen=True)
class OwnerUserId(UUID):
    """Identificador externo del usuario dueño. No es una FK a otro contexto."""
