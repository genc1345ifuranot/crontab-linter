"""Formatting helpers for ScheduleResult output."""

from __future__ import annotations

import json
from typing import Any, Dict

from .schedule import ScheduleResult

_DATE_FMT = "%Y-%m-%d %H:%M %Z"
_SUPPORTED_FORMATS = ("plain", "json")


def format_schedule_plain(result: ScheduleResult) -> str:
    """Return a human-readable string for *result*."""
    lines = [f"Expression : {result.expression}", f"Timezone   : {result.timezone}"]
    if result.error:
        lines.append(f"Error      : {result.error}")
        return "\n".join(lines)
    if not result.next_runs:
        lines.append("Next runs  : (none found)")
    else:
        lines.append("Next runs  :")
        for i, dt in enumerate(result.next_runs, 1):
            lines.append(f"  {i}. {dt.strftime(_DATE_FMT)}")
    return "\n".join(lines)


def format_schedule_json(result: ScheduleResult) -> str:
    """Return a JSON string for *result*."""
    data: Dict[str, Any] = {
        "expression": result.expression,
        "timezone": result.timezone,
    }
    if result.error:
        data["error"] = result.error
    else:
        data["next_runs"] = [
            dt.strftime(_DATE_FMT) for dt in result.next_runs
        ]
    return json.dumps(data, indent=2)


def format_schedule(result: ScheduleResult, fmt: str = "plain") -> str:
    """Dispatch to the appropriate formatter.

    Args:
        result: The schedule result to format.
        fmt: Output format; one of ``"plain"`` or ``"json"``.

    Raises:
        ValueError: If *fmt* is not a supported format string.
    """
    if fmt not in _SUPPORTED_FORMATS:
        raise ValueError(
            f"Unsupported format {fmt!r}. Expected one of: {', '.join(_SUPPORTED_FORMATS)}"
        )
    if fmt == "json":
        return format_schedule_json(result)
    return format_schedule_plain(result)
