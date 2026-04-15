"""Compare two crontab expressions and highlight differences."""

from dataclasses import dataclass, field
from typing import List, Optional

from .parser import CronExpression, parse
from .explainer import explain


@dataclass
class FieldDiff:
    name: str
    old_value: str
    new_value: str
    changed: bool


@dataclass
class CronDiff:
    old_expr: str
    new_expr: str
    fields: List[FieldDiff] = field(default_factory=list)
    old_explanation: str = ""
    new_explanation: str = ""

    @property
    def has_changes(self) -> bool:
        return any(f.changed for f in self.fields)

    @property
    def changed_fields(self) -> List[FieldDiff]:
        return [f for f in self.fields if f.changed]


FIELD_NAMES = ["minute", "hour", "day_of_month", "month", "day_of_week"]


def diff_expressions(old: str, new: str) -> CronDiff:
    """Compare two crontab expressions and return a CronDiff."""
    old_parsed: CronExpression = parse(old)
    new_parsed: CronExpression = parse(new)

    old_parts = old_parsed.raw.split()
    new_parts = new_parsed.raw.split()

    fields: List[FieldDiff] = []
    for i, name in enumerate(FIELD_NAMES):
        old_val = old_parts[i] if i < len(old_parts) else "*"
        new_val = new_parts[i] if i < len(new_parts) else "*"
        fields.append(FieldDiff(
            name=name,
            old_value=old_val,
            new_value=new_val,
            changed=(old_val != new_val),
        ))

    return CronDiff(
        old_expr=old,
        new_expr=new,
        fields=fields,
        old_explanation=explain(old_parsed),
        new_explanation=explain(new_parsed),
    )
