"""Detect scheduling overlaps between multiple cron expressions."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Tuple

from .parser import CronExpression, parse
from .schedule import _matches

import datetime


@dataclass
class OverlapPair:
    expr_a: str
    expr_b: str
    sample_times: List[datetime.datetime] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "expr_a": self.expr_a,
            "expr_b": self.expr_b,
            "sample_times": [t.isoformat() for t in self.sample_times],
        }


@dataclass
class OverlapResult:
    pairs: List[OverlapPair] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    @property
    def has_overlaps(self) -> bool:
        return bool(self.pairs)

    def to_dict(self) -> dict:
        return {
            "has_overlaps": self.has_overlaps,
            "pairs": [p.to_dict() for p in self.pairs],
            "errors": self.errors,
        }


def _parse_safe(expr: str):
    try:
        return parse(expr)
    except Exception:
        return None


def _sample_overlap(
    a: CronExpression,
    b: CronExpression,
    start: datetime.datetime,
    minutes: int = 1440,
) -> List[datetime.datetime]:
    """Return up to 5 minutes where both expressions fire."""
    hits: List[datetime.datetime] = []
    current = start.replace(second=0, microsecond=0)
    for _ in range(minutes):
        if _matches(a, current) and _matches(b, current):
            hits.append(current)
            if len(hits) >= 5:
                break
        current += datetime.timedelta(minutes=1)
    return hits


def find_overlaps(
    expressions: List[str],
    start: datetime.datetime | None = None,
    minutes: int = 1440,
) -> OverlapResult:
    """Find all pairs of expressions that fire at the same time."""
    if start is None:
        start = datetime.datetime.now().replace(second=0, microsecond=0)

    result = OverlapResult()
    parsed: List[Tuple[str, CronExpression | None]] = []

    for expr in expressions:
        p = _parse_safe(expr)
        if p is None:
            result.errors.append(f"Invalid expression: {expr!r}")
        parsed.append((expr, p))

    for i in range(len(parsed)):
        for j in range(i + 1, len(parsed)):
            expr_a, pa = parsed[i]
            expr_b, pb = parsed[j]
            if pa is None or pb is None:
                continue
            samples = _sample_overlap(pa, pb, start, minutes)
            if samples:
                result.pairs.append(OverlapPair(expr_a, expr_b, samples))

    return result
