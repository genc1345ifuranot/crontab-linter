"""Format OverlapResult for plain-text and JSON output."""
from __future__ import annotations

import json
from .overlap import OverlapResult


def format_overlap_plain(result: OverlapResult) -> str:
    lines: list[str] = []

    if result.errors:
        for err in result.errors:
            lines.append(f"  ERROR: {err}")

    if not result.has_overlaps:
        lines.append("No scheduling overlaps detected.")
        return "\n".join(lines)

    lines.append(f"Found {len(result.pairs)} overlapping pair(s):")
    for pair in result.pairs:
        lines.append(f"  {pair.expr_a!r}  <->  {pair.expr_b!r}")
        for t in pair.sample_times:
            lines.append(f"    overlaps at: {t.strftime('%Y-%m-%d %H:%M')}")

    return "\n".join(lines)


def format_overlap_json(result: OverlapResult) -> str:
    return json.dumps(result.to_dict(), indent=2)


def format_overlap(result: OverlapResult, fmt: str = "plain") -> str:
    if fmt == "json":
        return format_overlap_json(result)
    return format_overlap_plain(result)
