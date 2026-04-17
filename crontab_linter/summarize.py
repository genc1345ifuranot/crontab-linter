"""Summarize a crontab expression into a human-readable schedule category."""
from dataclasses import dataclass
from typing import Optional
from crontab_linter.parser import CronExpression, parse
from crontab_linter.validator import validate


@dataclass
class SummaryResult:
    expression: str
    category: str
    description: str
    valid: bool
    error: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "expression": self.expression,
            "category": self.category,
            "description": self.description,
            "valid": self.valid,
            "error": self.error,
        }


def _categorize(expr: CronExpression) -> tuple[str, str]:
    minute = expr.minute.raw
    hour = expr.hour.raw
    dom = expr.day_of_month.raw
    month = expr.month.raw
    dow = expr.day_of_week.raw

    if all(f == "*" for f in [minute, hour, dom, month, dow]):
        return "every-minute", "Runs every minute"

    if minute != "*" and hour != "*" and dom == "*" and month == "*" and dow == "*":
        return "daily", f"Runs daily at {hour}:{minute.zfill(2)}"

    if minute != "*" and hour != "*" and dom == "*" and month == "*" and dow != "*":
        return "weekly", f"Runs weekly on day-of-week {dow} at {hour}:{minute.zfill(2)}"

    if minute != "*" and hour != "*" and dom != "*" and month == "*" and dow == "*":
        return "monthly", f"Runs monthly on day {dom} at {hour}:{minute.zfill(2)}"

    if minute != "*" and hour != "*" and dom != "*" and month != "*" and dow == "*":
        return "yearly", f"Runs yearly in month {month} on day {dom} at {hour}:{minute.zfill(2)}"

    if minute.startswith("*/") and hour == "*":
        step = minute[2:]
        return "interval", f"Runs every {step} minute(s)"

    if minute == "*" and hour.startswith("*/"):
        step = hour[2:]
        return "interval", f"Runs every {step} hour(s)"

    return "custom", "Custom schedule"


def summarize(expression: str) -> SummaryResult:
    try:
        expr = parse(expression)
    except Exception as exc:
        return SummaryResult(expression=expression, category="invalid", description="", valid=False, error=str(exc))

    result = validate(expr)
    if not result.valid:
        return SummaryResult(
            expression=expression,
            category="invalid",
            description="",
            valid=False,
            error="; ".join(result.errors),
        )

    category, description = _categorize(expr)
    return SummaryResult(expression=expression, category=category, description=description, valid=True)
