"""Crontab expression parser module."""

from dataclasses import dataclass
from typing import List, Optional


CRON_FIELDS = ["minute", "hour", "day_of_month", "month", "day_of_week"]

FIELD_RANGES = {
    "minute": (0, 59),
    "hour": (0, 23),
    "day_of_month": (1, 31),
    "month": (1, 12),
    "day_of_week": (0, 7),
}

MONTH_ALIASES = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4,
    "may": 5, "jun": 6, "jul": 7, "aug": 8,
    "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}

DOW_ALIASES = {
    "sun": 0, "mon": 1, "tue": 2, "wed": 3,
    "thu": 4, "fri": 5, "sat": 6,
}


@dataclass
class CronField:
    name: str
    raw: str
    values: List[int]


@dataclass
class CronExpression:
    raw: str
    fields: List[CronField]

    @property
    def minute(self) -> CronField:
        return self.fields[0]

    @property
    def hour(self) -> CronField:
        return self.fields[1]

    @property
    def day_of_month(self) -> CronField:
        return self.fields[2]

    @property
    def month(self) -> CronField:
        return self.fields[3]

    @property
    def day_of_week(self) -> CronField:
        return self.fields[4]


def _resolve_aliases(value: str, aliases: dict) -> str:
    for alias, num in aliases.items():
        value = value.lower().replace(alias, str(num))
    return value


def _expand_field(raw: str, field_name: str) -> List[int]:
    aliases = MONTH_ALIASES if field_name == "month" else DOW_ALIASES
    raw = _resolve_aliases(raw, aliases)
    min_val, max_val = FIELD_RANGES[field_name]
    values = set()

    for part in raw.split(","):
        if part == "*":
            values.update(range(min_val, max_val + 1))
        elif "/" in part:
            base, step = part.split("/", 1)
            step = int(step)
            start = min_val if base == "*" else int(base.split("-")[0])
            end = max_val if base == "*" else (int(base.split("-")[1]) if "-" in base else max_val)
            values.update(range(start, end + 1, step))
        elif "-" in part:
            start, end = part.split("-", 1)
            values.update(range(int(start), int(end) + 1))
        else:
            values.add(int(part))

    return sorted(values)


def parse(expression: str) -> Optional[CronExpression]:
    """Parse a crontab expression string into a CronExpression object."""
    parts = expression.strip().split()
    if len(parts) != 5:
        return None

    fields = [
        CronField(name=name, raw=raw, values=_expand_field(raw, name))
        for name, raw in zip(CRON_FIELDS, parts)
    ]
    return CronExpression(raw=expression, fields=fields)
