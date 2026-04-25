"""Forecast: predict next N run times with human-readable labels."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional

from .parser import CronExpression
from .schedule import next_runs


@dataclass
class ForecastEntry:
    dt: datetime
    label: str

    def to_dict(self) -> dict:
        return {"datetime": self.dt.isoformat(), "label": self.label}


@dataclass
class ForecastResult:
    expression: str
    timezone: str
    entries: List[ForecastEntry] = field(default_factory=list)
    error: Optional[str] = None

    @property
    def ok(self) -> bool:
        return self.error is None

    def to_dict(self) -> dict:
        return {
            "expression": self.expression,
            "timezone": self.timezone,
            "ok": self.ok,
            "error": self.error,
            "entries": [e.to_dict() for e in self.entries],
        }


_LABELS = [
    "1st", "2nd", "3rd", "4th", "5th",
    "6th", "7th", "8th", "9th", "10th",
]


def _ordinal(n: int) -> str:
    if n <= len(_LABELS):
        return _LABELS[n - 1]
    suffix = "th" if 11 <= (n % 100) <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


def compute_forecast(
    expr: CronExpression,
    count: int = 5,
    tz_name: str = "UTC",
    after: Optional[datetime] = None,
) -> ForecastResult:
    """Return the next *count* scheduled datetimes with ordinal labels."""
    if after is None:
        after = datetime.now(tz=timezone.utc)

    try:
        runs = next_runs(expr, count=count, tz_name=tz_name, after=after)
    except Exception as exc:  # noqa: BLE001
        return ForecastResult(
            expression=" ".join([
                expr.minute.raw, expr.hour.raw, expr.day_of_month.raw,
                expr.month.raw, expr.day_of_week.raw,
            ]),
            timezone=tz_name,
            error=str(exc),
        )

    entries = [
        ForecastEntry(dt=dt, label=f"{_ordinal(i + 1)} run")
        for i, dt in enumerate(runs)
    ]
    raw = " ".join([
        expr.minute.raw, expr.hour.raw, expr.day_of_month.raw,
        expr.month.raw, expr.day_of_week.raw,
    ])
    return ForecastResult(expression=raw, timezone=tz_name, entries=entries)
