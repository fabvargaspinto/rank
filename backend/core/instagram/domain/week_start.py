from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta

from core.shared.domain.domain_error import InvalidDateError


@dataclass(frozen=True)
class WeekStart:
    """Lunes 00:00 UTC de la semana ISO a la que pertenece una captura."""

    value: date

    def __post_init__(self) -> None:
        if not isinstance(self.value, date) or isinstance(self.value, datetime):
            raise InvalidDateError("El inicio de semana no es válido")
        if self.value.weekday() != 0:
            raise InvalidDateError("El inicio de semana tiene que ser un lunes")

    @classmethod
    def from_datetime(cls, moment: datetime) -> WeekStart:
        if moment.tzinfo is None or moment.utcoffset() is None:
            raise InvalidDateError("La fecha no es válida")
        utc_moment = moment.astimezone(UTC)
        monday = utc_moment.date() - timedelta(days=utc_moment.weekday())
        return cls(monday)

    def to_isoformat(self) -> str:
        return self.value.isoformat()

    @classmethod
    def from_isoformat(cls, value: str | date) -> WeekStart:
        if isinstance(value, datetime):
            raise InvalidDateError("El inicio de semana no es válido")
        if isinstance(value, date):
            return cls(value)
        return cls(date.fromisoformat(value))
