"""Compute a complexity score for a cron expression."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from .parser import CronExpression, parse


@dataclass
class ComplexityResult:
    expression: str
    score: int
    level: str          # "simple" | "moderate" | "complex"
    reasons: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "expression": self.expression,
            "score": self.score,
            "level": self.level,
            "reasons": self.reasons,
        }


def _field_score(value: str, name: str) -> tuple[int, list[str]]:
    """Return (points, reasons) for a single cron field string."""
    points = 0
    reasons: list[str] = []

    if value == "*":
        return 0, []

    if "," in value:
        count = value.count(",") + 1
        points += count
        reasons.append(f"{name} uses a list with {count} values (+{count})")

    if "/" in value:
        points += 2
        reasons.append(f"{name} uses a step expression (+2)")

    if "-" in value and "/" not in value:
        points += 1
        reasons.append(f"{name} uses a range (+1)")

    if value not in ("*",) and "," not in value and "/" not in value and "-" not in value:
        # plain specific value
        points += 1
        reasons.append(f"{name} is fixed to a specific value (+1)")

    return points, reasons


def _level(score: int) -> str:
    if score <= 3:
        return "simple"
    if score <= 7:
        return "moderate"
    return "complex"


def compute_complexity(expression: str) -> ComplexityResult:
    """Parse *expression* and return a :class:`ComplexityResult`."""
    expr: CronExpression = parse(expression)

    fields = [
        (expr.minute, "minute"),
        (expr.hour, "hour"),
        (expr.day_of_month, "day_of_month"),
        (expr.month, "month"),
        (expr.day_of_week, "day_of_week"),
    ]

    total = 0
    all_reasons: list[str] = []

    for fld, name in fields:
        pts, rsns = _field_score(fld.raw, name)
        total += pts
        all_reasons.extend(rsns)

    return ComplexityResult(
        expression=expression,
        score=total,
        level=_level(total),
        reasons=all_reasons,
    )
