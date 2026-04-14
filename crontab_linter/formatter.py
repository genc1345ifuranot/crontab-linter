"""Output formatters for crontab-linter results."""
from dataclasses import dataclass
from typing import Optional
from crontab_linter.validator import ValidationResult
from crontab_linter.timezone import TimezoneCheckResult


@dataclass
class FormattedOutput:
    expression: str
    is_valid: bool
    explanation: Optional[str]
    warnings: list
    errors: list
    timezone_info: Optional[str]


def format_plain(result: FormattedOutput) -> str:
    """Format output as plain text."""
    lines = []
    status = "VALID" if result.is_valid else "INVALID"
    lines.append(f"Expression : {result.expression}")
    lines.append(f"Status     : {status}")

    if result.explanation:
        lines.append(f"Explanation: {result.explanation}")

    if result.timezone_info:
        lines.append(f"Timezone   : {result.timezone_info}")

    for err in result.errors:
        lines.append(f"[ERROR]    {err}")

    for warn in result.warnings:
        lines.append(f"[WARN]     {warn}")

    return "\n".join(lines)


def format_json(result: FormattedOutput) -> str:
    """Format output as JSON string."""
    import json
    data = {
        "expression": result.expression,
        "valid": result.is_valid,
        "explanation": result.explanation,
        "timezone": result.timezone_info,
        "errors": result.errors,
        "warnings": result.warnings,
    }
    return json.dumps(data, indent=2)


def build_output(
    expression: str,
    validation: ValidationResult,
    explanation: Optional[str],
    tz_result: Optional[TimezoneCheckResult] = None,
) -> FormattedOutput:
    """Assemble a FormattedOutput from individual results."""
    tz_info = None
    warnings = list(validation.warnings)

    if tz_result is not None:
        if tz_result.is_valid:
            tz_info = tz_result.timezone
        else:
            warnings.append(f"Timezone issue: {tz_result.message}")

        if tz_result.dst_ambiguous:
            warnings.append(f"DST ambiguity: {tz_result.dst_message}")

    return FormattedOutput(
        expression=expression,
        is_valid=validation.is_valid,
        explanation=explanation,
        warnings=warnings,
        errors=list(validation.errors),
        timezone_info=tz_info,
    )
