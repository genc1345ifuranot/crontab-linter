"""Human-readable explanation generator for crontab expressions."""

from typing import List

from crontab_linter.parser import CronExpression, CronField


MONTH_NAMES = [
    "", "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]

DOW_NAMES = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]


def _explain_field(cron_field: CronField, unit: str, names: List[str] = None) -> str:
    raw = cron_field.raw
    values = cron_field.values

    if raw == "*":
        return f"every {unit}"

    if "/" in raw and raw.startswith("*/"):
        step = raw.split("/")[1]
        return f"every {step} {unit}s"

    if names:
        labeled = [names[v] if 0 <= v < len(names) else str(v) for v in values]
    else:
        labeled = [str(v) for v in values]

    if len(labeled) == 1:
        return f"{unit} {labeled[0]}"
    return f"{unit}s {', '.join(labeled[:-1])} and {labeled[-1]}"


def explain(expr: CronExpression) -> str:
    """Generate a human-readable explanation of a parsed cron expression."""
    parts = []

    minute_str = _explain_field(expr.minute, "minute")
    hour_str = _explain_field(expr.hour, "hour")

    if expr.minute.raw == "*" and expr.hour.raw == "*":
        time_str = "every minute"
    elif expr.minute.raw == "0" and expr.hour.raw != "*":
        hour_vals = expr.hour.values
        hour_labels = [f"{h:02d}:00" for h in hour_vals]
        time_str = "at " + ", ".join(hour_labels)
    else:
        time_str = f"at {minute_str} past {hour_str}"

    parts.append(time_str)

    if expr.day_of_month.raw != "*":
        parts.append(_explain_field(expr.day_of_month, "day"))

    if expr.month.raw != "*":
        parts.append(_explain_field(expr.month, "month", MONTH_NAMES))

    if expr.day_of_week.raw != "*":
        dow_vals = [v % 7 for v in expr.day_of_week.values]
        dow_labels = [DOW_NAMES[v] for v in dow_vals]
        if len(dow_labels) == 1:
            parts.append(f"on {dow_labels[0]}"
                         )
        else:
            parts.append(f"on {', '.join(dow_labels[:-1])} and {dow_labels[-1]}")

    return "Runs " + ", ".join(parts) + "."
