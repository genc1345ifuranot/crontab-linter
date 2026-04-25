"""Formatters for InterpolateResult."""
from __future__ import annotations

import json

from .interpolate import InterpolateResult


def format_interpolate_plain(result: InterpolateResult) -> str:
    lines: list[str] = []
    lines.append(f"Original   : {result.original}")
    lines.append(f"Interpolated: {result.interpolated}")
    if result.variables_used:
        lines.append("Variables used: " + ", ".join(result.variables_used))
    else:
        lines.append("Variables used: (none)")
    if result.missing_variables:
        lines.append("Missing variables: " + ", ".join(result.missing_variables))
        lines.append("Status: INCOMPLETE — unresolved placeholders remain")
    else:
        lines.append("Status: OK")
    return "\n".join(lines)


def format_interpolate_json(result: InterpolateResult) -> str:
    return json.dumps(result.to_dict(), indent=2)


def format_interpolate(result: InterpolateResult, fmt: str = "plain") -> str:
    if fmt == "json":
        return format_interpolate_json(result)
    return format_interpolate_plain(result)
