from datetime import UTC, datetime

import pytest

from core.instagram.domain.week_start import WeekStart
from core.shared.domain.domain_error import InvalidDateError


class TestWeekStart:
    def test_monday_stays_monday(self):
        week = WeekStart.from_datetime(datetime(2026, 10, 5, 0, 0, tzinfo=UTC))

        assert week.value.isoformat() == "2026-10-05"

    def test_normalizes_any_weekday_to_monday(self):
        week = WeekStart.from_datetime(datetime(2026, 10, 9, 18, 45, tzinfo=UTC))

        assert week.value.isoformat() == "2026-10-05"

    def test_rejects_a_date_that_is_not_monday(self):
        with pytest.raises(InvalidDateError):
            WeekStart.from_isoformat("2026-10-06")

    def test_round_trips_iso_date(self):
        week = WeekStart.from_isoformat("2026-10-05")

        assert week.to_isoformat() == "2026-10-05"
