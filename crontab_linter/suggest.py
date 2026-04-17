"""Suggest fixes for invalid crontab expressions."""
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional

from .parser import CronExpression
from .validator import validate


@dataclass
class Suggestion:
    original: str
    fixed: str
    reason: str


@dataclass
class SuggestResult:
    expression: str
    suggestions: List[Suggestion]

    @property
    def has_suggestions(self) -> bool:
        return len(self.suggestions) > 0


def _clamp(value: str, lo: int, hi: int) -> str:
    try:
        n = int(value)
        return str(max(lo, min(hi, n)))
    except ValueError:
        return str(lo)


_FIELD_RANGES = [
    (0, 59),  # minute
    (0, 23),  # hour
    (1, 31),  # dom
    (1, 12),  # month
    (0, 7),   # dow
]

_FIELD_NAMES = ["minute", "hour", "day_of_month", "month", "day_of_week"]


def _fix_field(raw: str, lo: int, hi: int) -> Optional[str]:
    """Return a clamped version of a field token if it's out of range."""
    if raw == "*":
        return None
    if raw.startswith("*/"):
        step = raw[2:]
        fixed_step = _clamp(step, 1, hi)
        return f"*/{fixed_step}" if fixed_step != step else None
    if "-" in raw:
        parts = raw.split("-", 1)
        a = _clamp(parts[0], lo, hi)
        b = _clamp(parts[1], lo, hi)
        fixed = f"{a}-{b}"
        return fixed if fixed != raw else None
    fixed = _clamp(raw, lo, hi)
    return fixed if fixed != raw else None


def suggest(expression: str) -> SuggestResult:
    suggestions: List[Suggestion] = []
    result = validate(expression)
    if result.is_valid:
        return SuggestResult(expression=expression, suggestions=[])

    parts = expression.strip().split()
    if len(parts) != 5:
        # Suggest wildcard fill
        while len(parts) < 5:
            parts.append("*")
        parts = parts[:5]
        fixed = " ".join(parts)
        suggestions.append(Suggestion(original=expression, fixed=fixed, reason="Padded missing fields with wildcard"))
        return SuggestResult(expression=expression, suggestions=suggestions)

    fixed_parts = list(parts)
    for i, (lo, hi) in enumerate(_FIELD_RANGES):
        fix = _fix_field(parts[i], lo, hi)
        if fix is not None:
            suggestions.append(Suggestion(
                original=parts[i],
                fixed=fix,
                reason=f"{_FIELD_NAMES[i]} value '{parts[i]}' out of range [{lo},{hi}], clamped to '{fix}'"
            ))
            fixed_parts[i] = fix

    return SuggestResult(expression=expression, suggestions=suggestions)
