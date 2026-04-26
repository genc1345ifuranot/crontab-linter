"""Compress a cron expression by replacing redundant fields with wildcards."""
from dataclasses import dataclass, field
from typing import List, Optional
from .parser import CronExpression, parse
from .validator import validate


@dataclass
class FieldCompression:
    name: str
    original: str
    compressed: str
    reason: str

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "original": self.original,
            "compressed": self.compressed,
            "reason": self.reason,
        }


@dataclass
class CompressResult:
    original: str
    compressed: str
    changes: List[FieldCompression] = field(default_factory=list)
    error: Optional[str] = None

    @property
    def ok(self) -> bool:
        return self.error is None

    @property
    def has_changes(self) -> bool:
        return len(self.changes) > 0

    def to_dict(self) -> dict:
        return {
            "original": self.original,
            "compressed": self.compressed,
            "ok": self.ok,
            "has_changes": self.has_changes,
            "changes": [c.to_dict() for c in self.changes],
            "error": self.error,
        }


_FIELD_NAMES = ["minute", "hour", "day_of_month", "month", "day_of_week"]
_FIELD_RANGES = {
    "minute": (0, 59),
    "hour": (0, 23),
    "day_of_month": (1, 31),
    "month": (1, 12),
    "day_of_week": (0, 6),
}


def _is_full_step(value: str, lo: int, hi: int) -> bool:
    """Return True if a step expression covers the full range (e.g. */1)."""
    if value.startswith("*/"):
        try:
            step = int(value[2:])
            return step == 1
        except ValueError:
            return False
    if "-" in value and "/" in value:
        try:
            range_part, step_part = value.rsplit("/", 1)
            start, end = range_part.split("-", 1)
            return int(start) == lo and int(end) == hi and int(step_part) == 1
        except ValueError:
            return False
    return False


def _is_full_range(value: str, lo: int, hi: int) -> bool:
    """Return True if a range expression spans the full field range."""
    if "-" not in value or "/" in value:
        return False
    try:
        start, end = value.split("-", 1)
        return int(start) == lo and int(end) == hi
    except ValueError:
        return False


def compress(expression: str) -> CompressResult:
    """Compress a cron expression, replacing redundant fields with '*'."""
    validation = validate(expression)
    if not validation.valid:
        return CompressResult(
            original=expression,
            compressed=expression,
            error="; ".join(validation.errors),
        )

    expr: CronExpression = parse(expression)
    fields = [
        expr.minute,
        expr.hour,
        expr.day_of_month,
        expr.month,
        expr.day_of_week,
    ]
    compressed_parts: List[str] = []
    changes: List[FieldCompression] = []

    for fname, fobj in zip(_FIELD_NAMES, fields):
        raw = fobj.raw
        lo, hi = _FIELD_RANGES[fname]
        new_val = raw
        reason = ""

        if raw != "*":
            if _is_full_step(raw, lo, hi):
                new_val = "*"
                reason = f"{raw!r} is equivalent to '*' (step of 1 over full range)"
            elif _is_full_range(raw, lo, hi):
                new_val = "*"
                reason = f"{raw!r} is equivalent to '*' (full range {lo}-{hi})"

        if new_val != raw:
            changes.append(FieldCompression(
                name=fname,
                original=raw,
                compressed=new_val,
                reason=reason,
            ))
        compressed_parts.append(new_val)

    compressed = " ".join(compressed_parts)
    return CompressResult(
        original=expression,
        compressed=compressed,
        changes=changes,
    )
