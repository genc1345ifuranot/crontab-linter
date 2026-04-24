"""Heatmap: compute execution frequency distribution for a cron expression."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from crontab_linter.parser import CronExpression, parse
from crontab_linter.validator import validate


@dataclass
class HeatmapResult:
    expression: str
    valid: bool
    errors: List[str]
    # keys are hour strings "0".."23"; values are hit counts across all minutes
    hourly: Dict[str, int] = field(default_factory=dict)
    # keys are minute strings "0".."59"
    minutely: Dict[str, int] = field(default_factory=dict)
    total_hits_per_day: int = 0

    def to_dict(self) -> dict:
        return {
            "expression": self.expression,
            "valid": self.valid,
            "errors": self.errors,
            "hourly": self.hourly,
            "minutely": self.minutely,
            "total_hits_per_day": self.total_hits_per_day,
        }


def _expand_field(raw: str, lo: int, hi: int) -> List[int]:
    """Return the list of integers matched by a single cron field token."""
    values: List[int] = []
    for part in raw.split(","):
        if part == "*":
            values.extend(range(lo, hi + 1))
        elif "/" in part:
            base, step = part.split("/", 1)
            start = lo if base == "*" else int(base)
            values.extend(range(start, hi + 1, int(step)))
        elif "-" in part:
            a, b = part.split("-", 1)
            values.extend(range(int(a), int(b) + 1))
        else:
            values.append(int(part))
    return sorted(set(v for v in values if lo <= v <= hi))


def compute_heatmap(expression: str) -> HeatmapResult:
    """Compute hourly and minutely hit distribution for *expression*."""
    result = validate(expression)
    if not result.valid:
        return HeatmapResult(
            expression=expression,
            valid=False,
            errors=result.errors,
        )

    expr: CronExpression = parse(expression)
    minutes = _expand_field(expr.minute, 0, 59)
    hours = _expand_field(expr.hour, 0, 23)

    hourly: Dict[str, int] = {str(h): 0 for h in range(24)}
    minutely: Dict[str, int] = {str(m): 0 for m in range(60)}

    for h in hours:
        hourly[str(h)] += len(minutes)
    for m in minutes:
        minutely[str(m)] += len(hours)

    total = len(hours) * len(minutes)

    return HeatmapResult(
        expression=expression,
        valid=True,
        errors=[],
        hourly=hourly,
        minutely=minutely,
        total_hits_per_day=total,
    )
