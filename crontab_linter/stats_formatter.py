"""Format StatsResult for plain-text and JSON output."""
from __future__ import annotations
import json
from .stats import StatsResult


def format_stats_plain(r: StatsResult) -> str:
    lines = [
        f"Total expressions : {r.total}",
        f"Valid             : {r.valid}",
        f"Invalid           : {r.invalid}  ({r.invalid_rate:.1%})",
        f"With warnings     : {r.with_warnings}  ({r.warning_rate:.1%})",
        f"Preset shortcuts  : {r.preset_count}",
        "",
        "Top values per field:",
    ]
    for fname, counts in r.field_frequency.items():
        if not counts:
            continue
        top = sorted(counts.items(), key=lambda x: -x[1])[:3]
        top_str = ", ".join(f"{v}({c})" for v, c in top)
        lines.append(f"  {fname:<14}: {top_str}")
    return "\n".join(lines)


def format_stats_json(r: StatsResult) -> str:
    data = {
        "total": r.total,
        "valid": r.valid,
        "invalid": r.invalid,
        "invalid_rate": r.invalid_rate,
        "with_warnings": r.with_warnings,
        "warning_rate": r.warning_rate,
        "preset_count": r.preset_count,
        "field_frequency": r.field_frequency,
    }
    return json.dumps(data, indent=2)


def format_stats(r: StatsResult, fmt: str = "plain") -> str:
    if fmt == "json":
        return format_stats_json(r)
    return format_stats_plain(r)
