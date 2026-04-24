"""Formatters for HeatmapResult."""
from __future__ import annotations

import json

from crontab_linter.heatmap import HeatmapResult

_BAR_CHARS = " ▁▂▃▄▅▆▇█"


def _bar(value: int, max_value: int, width: int = 8) -> str:
    if max_value == 0:
        return _BAR_CHARS[0] * width
    ratio = value / max_value
    filled = round(ratio * width)
    idx = min(len(_BAR_CHARS) - 1, max(0, round(ratio * (len(_BAR_CHARS) - 1))))
    return _BAR_CHARS[idx] * filled + " " * (width - filled)


def format_heatmap_plain(result: HeatmapResult) -> str:
    lines = [f"Heatmap for: {result.expression}"]
    if not result.valid:
        lines.append("  INVALID: " + "; ".join(result.errors))
        return "\n".join(lines)

    lines.append(f"  Total hits/day: {result.total_hits_per_day}")
    lines.append("")
    lines.append("  Hourly distribution (0–23):")
    max_h = max(result.hourly.values(), default=1) or 1
    for h in range(24):
        count = result.hourly.get(str(h), 0)
        bar = _bar(count, max_h)
        lines.append(f"    {h:02d}  {bar}  {count}")

    lines.append("")
    lines.append("  Minutely distribution (0–59):")
    max_m = max(result.minutely.values(), default=1) or 1
    for m in range(0, 60, 5):
        count = result.minutely.get(str(m), 0)
        bar = _bar(count, max_m)
        lines.append(f"    :{m:02d}  {bar}  {count}")

    return "\n".join(lines)


def format_heatmap_json(result: HeatmapResult) -> str:
    return json.dumps(result.to_dict(), indent=2)


def format_heatmap(result: HeatmapResult, fmt: str = "plain") -> str:
    if fmt == "json":
        return format_heatmap_json(result)
    return format_heatmap_plain(result)
