"""Reorder crontab fields into a canonical sorted representation.

For list-type fields (e.g. "5,3,1"), values are sorted numerically.
For all other field types the value is returned unchanged.
The result includes both the reordered expression string and a per-field
changed flag so callers can highlight what was normalised.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from .parser import CronExpression, parse


@dataclass
class FieldReorder:
    original: str
    reordered: str
    changed: bool

    def to_dict(self) -> dict:
        return {
            "original": self.original,
            "reordered": self.reordered,
            "changed": self.changed,
        }


@dataclass
class ReorderResult:
    original: str
    reordered: str
    fields: List[FieldReorder] = field(default_factory=list)
    ok: bool = True
    error: str = ""

    def has_changes(self) -> bool:
        return any(f.changed for f in self.fields)

    def to_dict(self) -> dict:
        return {
            "original": self.original,
            "reordered": self.reordered,
            "has_changes": self.has_changes(),
            "ok": self.ok,
            "error": self.error,
            "fields": [f.to_dict() for f in self.fields],
        }


def _reorder_field(value: str) -> str:
    """Sort comma-separated list values numerically; leave others unchanged."""
    if "," not in value:
        return value
    parts = value.split(",")
    try:
        sorted_parts = sorted(parts, key=lambda p: int(p))
    except ValueError:
        # Non-integer tokens (e.g. month aliases) — sort lexicographically
        sorted_parts = sorted(parts)
    return ",".join(sorted_parts)


def reorder(expression: str) -> ReorderResult:
    """Parse *expression* and return a ReorderResult with sorted list fields."""
    try:
        expr: CronExpression = parse(expression)
    except Exception as exc:  # noqa: BLE001
        return ReorderResult(original=expression, reordered=expression, ok=False, error=str(exc))

    raw_fields = [
        expr.minute,
        expr.hour,
        expr.day_of_month,
        expr.month,
        expr.day_of_week,
    ]

    field_reorders: List[FieldReorder] = []
    reordered_parts: List[str] = []

    for raw in raw_fields:
        original_val = raw.raw
        new_val = _reorder_field(original_val)
        field_reorders.append(FieldReorder(original=original_val, reordered=new_val, changed=(new_val != original_val)))
        reordered_parts.append(new_val)

    reordered_expr = " ".join(reordered_parts)
    return ReorderResult(
        original=expression,
        reordered=reordered_expr,
        fields=field_reorders,
        ok=True,
        error="",
    )
