"""Pivot analysis: group a list of cron expressions by a chosen field.

For each distinct value (or token) in the selected field, collect all
expressions that produce that value so callers can see which jobs share
a common schedule dimension.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .parser import CronExpression, parse
from .validator import validate


_FIELD_NAMES = ("minute", "hour", "day_of_month", "month", "day_of_week")


@dataclass
class PivotResult:
    pivot_field: str
    groups: Dict[str, List[str]]  # token -> [expression, ...]
    errors: List[str] = field(default_factory=list)

    @property
    def has_errors(self) -> bool:
        return bool(self.errors)

    def to_dict(self) -> dict:
        return {
            "pivot_field": self.pivot_field,
            "groups": self.groups,
            "errors": self.errors,
        }


def _field_token(expr: CronExpression, field_name: str) -> str:
    """Return the raw token string for *field_name* in *expr*."""
    f = getattr(expr, field_name)
    return f.raw


def pivot(
    expressions: List[str],
    pivot_field: str,
    *,
    skip_invalid: bool = True,
) -> PivotResult:
    """Group *expressions* by the raw token of *pivot_field*.

    Parameters
    ----------
    expressions:
        Raw cron expression strings (5-field standard format or presets).
    pivot_field:
        One of ``minute``, ``hour``, ``day_of_month``, ``month``,
        ``day_of_week``.
    skip_invalid:
        When *True* (default) invalid expressions are recorded in
        ``PivotResult.errors`` but do not abort the run.  When *False* the
        first invalid expression causes an immediate error entry and the
        expression is excluded from grouping regardless.
    """
    if pivot_field not in _FIELD_NAMES:
        return PivotResult(
            pivot_field=pivot_field,
            groups={},
            errors=[f"Unknown pivot field '{pivot_field}'. Choose from: {', '.join(_FIELD_NAMES)}"],
        )

    groups: Dict[str, List[str]] = {}
    errors: List[str] = []

    for raw in expressions:
        raw = raw.strip()
        if not raw or raw.startswith("#"):
            continue

        try:
            expr = parse(raw)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{raw!r}: parse error – {exc}")
            continue

        result = validate(expr)
        if not result.valid:
            msg = f"{raw!r}: " + "; ".join(result.errors)
            errors.append(msg)
            if not skip_invalid:
                continue
            # Even when skip_invalid=True we still exclude invalid ones
            continue

        token = _field_token(expr, pivot_field)
        groups.setdefault(token, []).append(raw)

    # Sort groups by key for deterministic output
    sorted_groups = dict(sorted(groups.items()))
    return PivotResult(pivot_field=pivot_field, groups=sorted_groups, errors=errors)
