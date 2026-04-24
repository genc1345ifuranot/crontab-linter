"""Compute how frequently a cron expression fires per day/hour/minute."""
from __future__ import annotations
from dataclasses import dataclass
from typing import List

from .parser import CronExpression, parse
from .validator import validate


@dataclass
class FrequencyResult:
    expression: str
    fires_per_day: float
    fires_per_hour: float
    fires_per_minute: float
    description: str
    valid: bool
    errors: List[str]

    def to_dict(self) -> dict:
        return {
            "expression": self.expression,
            "fires_per_day": self.fires_per_day,
            "fires_per_hour": self.fires_per_hour,
            "fires_per_minute": self.fires_per_minute,
            "description": self.description,
            "valid": self.valid,
            "errors": self.errors,
        }


def _count_values(field_str: str, min_val: int, max_val: int) -> int:
    """Return the number of distinct values a cron field matches."""
    if field_str == "*":
        return max_val - min_val + 1

    count = 0
    for part in field_str.split(","):
        if "/" in part:
            base, step = part.split("/", 1)
            step = int(step)
            if base == "*":
                start, end = min_val, max_val
            elif "-" in base:
                start, end = (int(x) for x in base.split("-", 1))
            else:
                start = int(base)
                end = max_val
            count += len(range(start, end + 1, step))
        elif "-" in part:
            start, end = (int(x) for x in part.split("-", 1))
            count += end - start + 1
        else:
            count += 1
    return count


def compute_frequency(expression: str) -> FrequencyResult:
    """Analyse how often *expression* fires."""
    validation = validate(expression)
    if not validation.valid:
        return FrequencyResult(
            expression=expression,
            fires_per_day=0.0,
            fires_per_hour=0.0,
            fires_per_minute=0.0,
            description="invalid expression",
            valid=False,
            errors=validation.errors,
        )

    expr: CronExpression = parse(expression)

    minutes_per_hour = _count_values(expr.minute, 0, 59)
    hours_per_day = _count_values(expr.hour, 0, 23)
    days_per_month = _count_values(expr.day_of_month, 1, 31)
    months_per_year = _count_values(expr.month, 1, 12)

    # Average days per year the job runs
    avg_days_per_year = days_per_month * months_per_year
    avg_days_per_day = avg_days_per_year / 365.0

    fires_per_day = round(hours_per_day * minutes_per_hour * avg_days_per_day, 4)
    fires_per_hour = round(minutes_per_hour * avg_days_per_day, 4)
    fires_per_minute = round(fires_per_day / 1440, 6)

    if fires_per_day >= 1440:
        desc = "every minute"
    elif fires_per_day >= 24:
        desc = f"~{int(fires_per_day)} times/day"
    elif fires_per_day >= 1:
        desc = f"~{int(fires_per_day)} time(s)/day"
    else:
        desc = "less than once a day"

    return FrequencyResult(
        expression=expression,
        fires_per_day=fires_per_day,
        fires_per_hour=fires_per_hour,
        fires_per_minute=fires_per_minute,
        description=desc,
        valid=True,
        errors=[],
    )
