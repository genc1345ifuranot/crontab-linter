"""Formatters for CoverageResult."""
from __future__ import annotations

import json

from .coverage import CoverageResult

_FIELD_ORDER = ["minute", "hour", "day_of_month", "month", "day_of_week"]


def format_coverage_plain(result: CoverageResult) -> str:
    lines: list[str] = []
    if not result.ok:
        lines.append(f"ERROR: {result.error}")
        return "\n".join(lines)

    lines.append(f"Expression : {result.expression}")
    lines.append(f"Overall    : {result.overall_ratio * 100:.1f}%")
    lines.append("")
    lines.append(f"{'Field':<16} {'Covered':>8} {'Total':>7} {'Ratio':>8}")
    lines.append("-" * 42)
    for name in _FIELD_ORDER:
        fc = result.fields[name]
        lines.append(
            f"{name:<16} {fc.covered:>8} {fc.total:>7} {fc.ratio * 100:>7.1f}%"
        )
    return "\n".join(lines)


def format_coverage_json(result: CoverageResult) -> str:
    return json.dumps(result.to_dict(), indent=2)


def format_coverage(result: CoverageResult, fmt: str = "plain") -> str:
    if fmt == "json":
        return format_coverage_json(result)
    return format_coverage_plain(result)
