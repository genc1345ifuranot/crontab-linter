"""Compute how much a cron expression deviates from a known baseline."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from .parser import CronExpression, parse
from .validator import validate


@dataclass
class FieldDeviation:
    name: str
    baseline: str
    candidate: str
    changed: bool

    def to_dict(self) -> dict:
        return {
            "field": self.name,
            "baseline": self.baseline,
            "candidate": self.candidate,
            "changed": self.changed,
        }


@dataclass
class DeviationResult:
    baseline_expr: str
    candidate_expr: str
    fields: List[FieldDeviation] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    deviation_score: int = 0

    @property
    def ok(self) -> bool:
        return not self.errors

    @property
    def has_deviation(self) -> bool:
        return self.deviation_score > 0

    def to_dict(self) -> dict:
        return {
            "baseline": self.baseline_expr,
            "candidate": self.candidate_expr,
            "ok": self.ok,
            "deviation_score": self.deviation_score,
            "has_deviation": self.has_deviation,
            "fields": [f.to_dict() for f in self.fields],
            "errors": self.errors,
        }


def _field_names() -> List[str]:
    return ["minute", "hour", "day_of_month", "month", "day_of_week"]


def compute_deviation(baseline: str, candidate: str) -> DeviationResult:
    result = DeviationResult(baseline_expr=baseline, candidate_expr=candidate)

    b_parsed: Optional[CronExpression] = None
    c_parsed: Optional[CronExpression] = None

    try:
        b_parsed = parse(baseline)
    except Exception as exc:  # noqa: BLE001
        result.errors.append(f"baseline parse error: {exc}")

    try:
        c_parsed = parse(candidate)
    except Exception as exc:  # noqa: BLE001
        result.errors.append(f"candidate parse error: {exc}")

    if b_parsed is None or c_parsed is None:
        return result

    b_val = validate(b_parsed)
    c_val = validate(c_parsed)

    if not b_val.valid:
        result.errors.extend([f"baseline: {e}" for e in b_val.errors])
    if not c_val.valid:
        result.errors.extend([f"candidate: {e}" for e in c_val.errors])

    if result.errors:
        return result

    names = _field_names()
    b_fields = [b_parsed.minute, b_parsed.hour, b_parsed.day_of_month, b_parsed.month, b_parsed.day_of_week]
    c_fields = [c_parsed.minute, c_parsed.hour, c_parsed.day_of_month, c_parsed.month, c_parsed.day_of_week]

    for name, bf, cf in zip(names, b_fields, c_fields):
        changed = bf.raw != cf.raw
        result.fields.append(FieldDeviation(name=name, baseline=bf.raw, candidate=cf.raw, changed=changed))
        if changed:
            result.deviation_score += 1

    return result
