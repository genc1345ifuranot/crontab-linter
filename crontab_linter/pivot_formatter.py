"""Formatters for PivotResult."""
from __future__ import annotations

import json

from .pivot import PivotResult


def format_pivot_plain(result: PivotResult) -> str:
    lines: list[str] = [f"Pivot by: {result.pivot_field}"]

    if result.has_errors:
        lines.append("Errors:")
        for err in result.errors:
            lines.append(f"  ! {err}")

    if not result.groups:
        lines.append("  (no valid expressions to group)")
        return "\n".join(lines)

    lines.append("")
    for token, exprs in result.groups.items():
        lines.append(f"  [{token}]  ({len(exprs)} expression{'s' if len(exprs) != 1 else ''})")
        for expr in exprs:
            lines.append(f"    - {expr}")

    return "\n".join(lines)


def format_pivot_json(result: PivotResult) -> str:
    return json.dumps(result.to_dict(), indent=2)


def format_pivot(result: PivotResult, fmt: str = "plain") -> str:
    if fmt == "json":
        return format_pivot_json(result)
    return format_pivot_plain(result)
