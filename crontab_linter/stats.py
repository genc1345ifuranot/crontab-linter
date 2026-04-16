"""Aggregate statistics over a collection of cron expressions."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List

from .batch import batch_lint


@dataclass
class StatsResult:
    total: int = 0
    valid: int = 0
    invalid: int = 0
    with_warnings: int = 0
    preset_count: int = 0
    field_frequency: dict = field(default_factory=dict)

    @property
    def invalid_rate(self) -> float:
        return round(self.invalid / self.total, 4) if self.total else 0.0

    @property
    def warning_rate(self) -> float:
        return round(self.with_warnings / self.total, 4) if self.total else 0.0


def compute_stats(expressions: List[str]) -> StatsResult:
    """Compute aggregate stats for a list of raw cron expression strings."""
    from .presets import is_preset, resolve_preset
    from .lint_rules import lint
    from .parser import parse
    from .validator import validate

    result = StatsResult()
    freq: dict = {"minute": {}, "hour": {}, "day_of_month": {}, "month": {}, "day_of_week": {}}

    for raw in expressions:
        raw = raw.strip()
        if not raw or raw.startswith("#"):
            continue
        result.total += 1

        expr_str = resolve_preset(raw) if is_preset(raw) else raw
        if is_preset(raw):
            result.preset_count += 1

        try:
            expr = parse(expr_str)
        except Exception:
            result.invalid += 1
            continue

        vr = validate(expr)
        if not vr.valid:
            result.invalid += 1
            continue

        result.valid += 1
        lr = lint(expr)
        if lr.has_warnings:
            result.with_warnings += 1

        for fname in ("minute", "hour", "day_of_month", "month", "day_of_week"):
            val = str(getattr(expr, fname).raw)
            freq[fname][val] = freq[fname].get(val, 0) + 1

    result.field_frequency = freq
    return result
