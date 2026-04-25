"""Formatters for ForecastResult."""
from __future__ import annotations

import json

from .forecast import ForecastResult


def format_forecast_plain(result: ForecastResult) -> str:
    lines: list[str] = []
    lines.append(f"Expression : {result.expression}")
    lines.append(f"Timezone   : {result.timezone}")
    if not result.ok:
        lines.append(f"Error      : {result.error}")
        return "\n".join(lines)
    if not result.entries:
        lines.append("No upcoming runs found.")
        return "\n".join(lines)
    lines.append("Forecast   :")
    for entry in result.entries:
        ts = entry.dt.strftime("%Y-%m-%d %H:%M %Z")
        lines.append(f"  {entry.label:<10} {ts}")
    return "\n".join(lines)


def format_forecast_json(result: ForecastResult) -> str:
    return json.dumps(result.to_dict(), indent=2)


def format_forecast(result: ForecastResult, fmt: str = "plain") -> str:
    if fmt == "json":
        return format_forecast_json(result)
    return format_forecast_plain(result)
