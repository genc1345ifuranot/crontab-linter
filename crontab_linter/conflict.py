"""Detect scheduling conflicts between two cron expressions."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from .parser import CronExpression, parse
from .schedule import _matches

import datetime


@dataclass
class ConflictResult:
    expr_a: str
    expr_b: str
    valid: bool
    errors: List[str] = field(default_factory=list)
    overlap_times: List[datetime.datetime] = field(default_factory=list)
    message: str = ""

    @property
    def has_conflict(self) -> bool:
        return len(self.overlap_times) > 0

    def to_dict(self) -> dict:
        return {
            "expr_a": self.expr_a,
            "expr_b": self.expr_b,
            "valid": self.valid,
            "errors": self.errors,
            "has_conflict": self.has_conflict,
            "overlap_count": len(self.overlap_times),
            "overlap_times": [t.isoformat() for t in self.overlap_times],
            "message": self.message,
        }


def _parse_safe(expr: str):
    """Return (CronExpression, None) or (None, error_str)."""
    try:
        return parse(expr), None
    except Exception as exc:  # noqa: BLE001
        return None, str(exc)


def find_conflicts(
    expr_a: str,
    expr_b: str,
    *,
    window_hours: int = 24,
    start: Optional[datetime.datetime] = None,
    max_overlaps: int = 10,
) -> ConflictResult:
    """Find minutes where both expressions fire within *window_hours* of *start*."""
    start = start or datetime.datetime(2024, 1, 1, 0, 0)
    result = ConflictResult(expr_a=expr_a, expr_b=expr_b, valid=True)

    cron_a, err_a = _parse_safe(expr_a)
    cron_b, err_b = _parse_safe(expr_b)

    if err_a:
        result.valid = False
        result.errors.append(f"Expression A: {err_a}")
    if err_b:
        result.valid = False
        result.errors.append(f"Expression B: {err_b}")

    if not result.valid:
        return result

    total_minutes = window_hours * 60
    current = start.replace(second=0, microsecond=0)

    for _ in range(total_minutes):
        if _matches(cron_a, current) and _matches(cron_b, current):
            result.overlap_times.append(current)
            if len(result.overlap_times) >= max_overlaps:
                break
        current += datetime.timedelta(minutes=1)

    if result.has_conflict:
        result.message = (
            f"Found {len(result.overlap_times)} overlapping minute(s) "
            f"in a {window_hours}-hour window."
        )
    else:
        result.message = f"No conflicts found in a {window_hours}-hour window."

    return result
