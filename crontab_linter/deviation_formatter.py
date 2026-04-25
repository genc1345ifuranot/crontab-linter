"""Format DeviationResult for plain-text and JSON output."""
from __future__ import annotations

import json

from .deviation import DeviationResult


def format_deviation_plain(result: DeviationResult) -> str:
    lines: list[str] = []
    lines.append(f"Baseline : {result.baseline_expr}")
    lines.append(f"Candidate: {result.candidate_expr}")

    if not result.ok:
        lines.append("Errors:")
        for err in result.errors:
            lines.append(f"  - {err}")
        return "\n".join(lines)

    if not result.has_deviation:
        lines.append("No deviation — expressions are equivalent.")
        return "\n".join(lines)

    lines.append(f"Deviation score: {result.deviation_score}")
    lines.append("Changed fields:")
    for fd in result.fields:
        if fd.changed:
            lines.append(f"  {fd.name:15s}  {fd.baseline!r:>20}  ->  {fd.candidate!r}")

    unchanged = [fd.name for fd in result.fields if not fd.changed]
    if unchanged:
        lines.append("Unchanged fields: " + ", ".join(unchanged))

    return "\n".join(lines)


def format_deviation_json(result: DeviationResult) -> str:
    return json.dumps(result.to_dict(), indent=2)


def format_deviation(result: DeviationResult, fmt: str = "plain") -> str:
    if fmt == "json":
        return format_deviation_json(result)
    return format_deviation_plain(result)
