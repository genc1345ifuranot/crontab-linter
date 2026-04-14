"""Crontab expression validator module."""

from dataclasses import dataclass, field
from typing import List

from crontab_linter.parser import CronExpression, FIELD_RANGES, parse


@dataclass
class ValidationResult:
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


def _check_field_range(cron_field, field_name: str, errors: List[str]) -> None:
    min_val, max_val = FIELD_RANGES[field_name]
    for val in cron_field.values:
        if not (min_val <= val <= max_val):
            errors.append(
                f"Field '{field_name}' has out-of-range value {val} "
                f"(allowed: {min_val}-{max_val})."
            )


def _check_dom_dow_conflict(expr: CronExpression, warnings: List[str]) -> None:
    dom_is_wildcard = expr.day_of_month.raw == "*"
    dow_is_wildcard = expr.day_of_week.raw == "*"
    if not dom_is_wildcard and not dow_is_wildcard:
        warnings.append(
            "Both 'day_of_month' and 'day_of_week' are specified; "
            "cron will trigger when EITHER condition is met (OR logic)."
        )


def _check_unreachable_dom(expr: CronExpression, warnings: List[str]) -> None:
    months_with_30 = {2}
    months_with_30_days = {4, 6, 9, 11}
    dom_values = expr.day_of_month.values
    month_values = expr.month.values

    if 31 in dom_values:
        short_months = months_with_30 | months_with_30_days
        if all(m in short_months for m in month_values):
            warnings.append(
                "Day 31 is scheduled but selected months never have 31 days."
            )

    if 29 in dom_values or 30 in dom_values or 31 in dom_values:
        if month_values == [2]:
            warnings.append(
                "Scheduling on day 29-31 in February may be unreachable in non-leap years."
            )


def validate(expression: str) -> ValidationResult:
    """Validate a crontab expression string."""
    parts = expression.strip().split()
    if len(parts) != 5:
        return ValidationResult(
            is_valid=False,
            errors=[f"Expected 5 fields, got {len(parts)}. Format: minute hour dom month dow."]
        )

    expr = parse(expression)
    if expr is None:
        return ValidationResult(is_valid=False, errors=["Failed to parse expression."])

    errors: List[str] = []
    warnings: List[str] = []

    for cron_field in expr.fields:
        _check_field_range(cron_field, cron_field.name, errors)

    _check_dom_dow_conflict(expr, warnings)
    _check_unreachable_dom(expr, warnings)

    return ValidationResult(is_valid=len(errors) == 0, errors=errors, warnings=warnings)
