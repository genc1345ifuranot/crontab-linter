"""Truncate a cron expression by replacing specific fields with wildcards."""
from dataclasses import dataclass, field
from typing import List, Optional
from crontab_linter.parser import CronExpression, parse

FIELD_NAMES = ["minute", "hour", "day_of_month", "month", "day_of_week"]
FIELD_INDICES = {name: i for i, name in enumerate(FIELD_NAMES)}


@dataclass
class TruncateResult:
    original: str
    truncated: Optional[str]
    fields_cleared: List[str]
    errors: List[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors

    def to_dict(self) -> dict:
        return {
            "original": self.original,
            "truncated": self.truncated,
            "fields_cleared": self.fields_cleared,
            "ok": self.ok,
            "errors": self.errors,
        }


def truncate(expression: str, fields: List[str]) -> TruncateResult:
    """Replace the named fields in *expression* with '*'.

    Parameters
    ----------
    expression:
        A standard 5-part cron expression string.
    fields:
        Field names to wildcard, e.g. ["minute", "hour"].
    """
    unknown = [f for f in fields if f not in FIELD_INDICES]
    if unknown:
        return TruncateResult(
            original=expression,
            truncated=None,
            fields_cleared=[],
            errors=[f"Unknown field(s): {', '.join(unknown)}"],
        )

    try:
        expr: CronExpression = parse(expression)
    except ValueError as exc:
        return TruncateResult(
            original=expression,
            truncated=None,
            fields_cleared=[],
            errors=[str(exc)],
        )

    parts = [
        expr.minute.raw,
        expr.hour.raw,
        expr.day_of_month.raw,
        expr.month.raw,
        expr.day_of_week.raw,
    ]

    cleared: List[str] = []
    for fname in fields:
        idx = FIELD_INDICES[fname]
        if parts[idx] != "*":
            parts[idx] = "*"
            cleared.append(fname)

    return TruncateResult(
        original=expression,
        truncated=" ".join(parts),
        fields_cleared=cleared,
    )
