"""Compute time coverage metrics for a cron expression.

For each time dimension (minutes, hours, days-of-month, months,
days-of-week) we report what fraction of the valid range is
covered by the expression.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from .parser import CronExpression, parse
from .heatmap import _expand_field  # reuse existing expansion helper

_RANGES: Dict[str, range] = {
    "minute": range(0, 60),
    "hour": range(0, 24),
    "day_of_month": range(1, 32),
    "month": range(1, 13),
    "day_of_week": range(0, 7),
}


@dataclass
class FieldCoverage:
    name: str
    covered: int
    total: int
    ratio: float
    values: List[int]

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "covered": self.covered,
            "total": self.total,
            "ratio": round(self.ratio, 4),
            "values": self.values,
        }


@dataclass
class CoverageResult:
    expression: str
    fields: Dict[str, FieldCoverage] = field(default_factory=dict)
    overall_ratio: float = 0.0
    error: str = ""

    @property
    def ok(self) -> bool:
        return not self.error

    def to_dict(self) -> dict:
        return {
            "expression": self.expression,
            "ok": self.ok,
            "error": self.error,
            "overall_ratio": round(self.overall_ratio, 4),
            "fields": {k: v.to_dict() for k, v in self.fields.items()},
        }


def compute_coverage(expression: str) -> CoverageResult:
    """Return coverage metrics for *expression*."""
    try:
        expr: CronExpression = parse(expression)
    except ValueError as exc:
        return CoverageResult(expression=expression, error=str(exc))

    field_map = {
        "minute": expr.minute,
        "hour": expr.hour,
        "day_of_month": expr.day_of_month,
        "month": expr.month,
        "day_of_week": expr.day_of_week,
    }

    fields: Dict[str, FieldCoverage] = {}
    ratios: List[float] = []

    for name, cron_field in field_map.items():
        valid_range = _RANGES[name]
        values = sorted(_expand_field(cron_field, valid_range))
        total = len(valid_range)
        covered = len(values)
        ratio = covered / total if total else 0.0
        fields[name] = FieldCoverage(
            name=name,
            covered=covered,
            total=total,
            ratio=ratio,
            values=values,
        )
        ratios.append(ratio)

    overall = sum(ratios) / len(ratios) if ratios else 0.0
    return CoverageResult(
        expression=expression,
        fields=fields,
        overall_ratio=overall,
    )
