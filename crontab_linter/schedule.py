"""Next-run schedule calculator for cron expressions."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional

import pytz

from .parser import CronExpression


@dataclass
class ScheduleResult:
    expression: str
    timezone: str
    next_runs: List[datetime] = field(default_factory=list)
    error: Optional[str] = None

    def __repr__(self) -> str:  # pragma: no cover
        return f"ScheduleResult(expression={self.expression!r}, next_runs={self.next_runs})"


def _matches_field(value: int, cron_field) -> bool:
    """Return True if *value* satisfies *cron_field*."""
    if cron_field.raw == "*":
        return True
    for part in cron_field.raw.split(","):
        if "/" in part:
            base, step = part.split("/", 1)
            start = 0 if base == "*" else int(base)
            if value >= start and (value - start) % int(step) == 0:
                return True
        elif "-" in part:
            lo, hi = part.split("-", 1)
            if int(lo) <= value <= int(hi):
                return True
        else:
            if value == int(part):
                return True
    return False


def _matches(dt: datetime, expr: CronExpression) -> bool:
    """Return True if *dt* matches all five cron fields."""
    return (
        _matches_field(dt.minute, expr.minute)
        and _matches_field(dt.hour, expr.hour)
        and _matches_field(dt.day, expr.day_of_month)
        and _matches_field(dt.month, expr.month)
        and _matches_field(dt.weekday() + 1 if dt.weekday() < 6 else 0, expr.day_of_week)
    )


def next_runs(
    expr: CronExpression,
    timezone: str = "UTC",
    count: int = 5,
    start: Optional[datetime] = None,
) -> ScheduleResult:
    """Compute the next *count* run times for *expr* in *timezone*."""
    try:
        tz = pytz.timezone(timezone)
    except pytz.UnknownTimeZoneError:
        return ScheduleResult(
            expression=expr.raw,
            timezone=timezone,
            error=f"Unknown timezone: {timezone!r}",
        )

    now = start or datetime.now(tz=tz)
    # Advance one minute so we never return 'now' itself
    cursor = now.replace(second=0, microsecond=0) + timedelta(minutes=1)

    results: List[datetime] = []
    limit = count * 366 * 24 * 60  # safety cap
    steps = 0
    while len(results) < count and steps < limit:
        if _matches(cursor, expr):
            results.append(cursor)
        cursor += timedelta(minutes=1)
        steps += 1

    return ScheduleResult(
        expression=expr.raw,
        timezone=timezone,
        next_runs=results,
    )
