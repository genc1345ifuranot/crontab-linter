"""Format ConflictResult for plain-text and JSON output."""
from __future__ import annotations

import json

from .conflict import ConflictResult


def format_conflict_plain(result: ConflictResult) -> str:
    lines: list[str] = []
    lines.append(f"Expression A : {result.expr_a}")
    lines.append(f"Expression B : {result.expr_b}")

    if not result.valid:
        lines.append("Status       : INVALID")
        for err in result.errors:
            lines.append(f"  Error: {err}")
        return "\n".join(lines)

    status = "CONFLICT DETECTED" if result.has_conflict else "NO CONFLICT"
    lines.append(f"Status       : {status}")
    lines.append(f"Message      : {result.message}")

    if result.overlap_times:
        lines.append("Overlapping times:")
        for t in result.overlap_times:
            lines.append(f"  - {t.strftime('%Y-%m-%d %H:%M')}")

    return "\n".join(lines)


def format_conflict_json(result: ConflictResult) -> str:
    return json.dumps(result.to_dict(), indent=2)


def format_conflict(result: ConflictResult, fmt: str = "plain") -> str:
    if fmt == "json":
        return format_conflict_json(result)
    return format_conflict_plain(result)
