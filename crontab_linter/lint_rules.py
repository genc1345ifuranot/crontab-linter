"""Additional lint rules for crontab expressions."""
from dataclasses import dataclass, field
from typing import List
from crontab_linter.parser import CronExpression


@dataclass
class LintWarning:
    code: str
    message: str
    severity: str = "warning"  # "warning" | "info"

    def to_dict(self) -> dict:
        return {"code": self.code, "message": self.message, "severity": self.severity}


@dataclass
class LintResult:
    warnings: List[LintWarning] = field(default_factory=list)

    @property
    def has_warnings(self) -> bool:
        return len(self.warnings) > 0

    def to_dict(self) -> dict:
        return {"warnings": [w.to_dict() for w in self.warnings]}


def _check_every_minute(expr: CronExpression) -> List[LintWarning]:
    """Warn when job runs every minute."""
    if expr.minute.raw == "*" and expr.hour.raw == "*":
        return [LintWarning(
            code="EVERY_MINUTE",
            message="Job runs every minute — this may cause high system load.",
            severity="warning",
        )]
    return []


def _check_midnight_only(expr: CronExpression) -> List[LintWarning]:
    """Info when job runs only at midnight."""
    if expr.minute.raw == "0" and expr.hour.raw == "0":
        return [LintWarning(
            code="MIDNIGHT_ONLY",
            message="Job runs only at midnight (00:00). Ensure this is intentional.",
            severity="info",
        )]
    return []


def _check_high_frequency(expr: CronExpression) -> List[LintWarning]:
    """Warn on step values that produce very frequent runs (e.g. */1 or */2)."""
    warnings = []
    for fname in ("minute", "hour"):
        f = getattr(expr, fname)
        if f.raw.startswith("*/"):
            try:
                step = int(f.raw[2:])
            except ValueError:
                continue
            if fname == "minute" and step <= 2:
                warnings.append(LintWarning(
                    code="HIGH_FREQUENCY_MINUTE",
                    message=f"Minute field '{f.raw}' triggers very frequently ({60 // step}x/hour).",
                    severity="warning",
                ))
            if fname == "hour" and step == 1:
                warnings.append(LintWarning(
                    code="HIGH_FREQUENCY_HOUR",
                    message=f"Hour field '{f.raw}' is equivalent to '*' — consider using '*' directly.",
                    severity="info",
                ))
    return warnings


def _check_friday_13th_pattern(expr: CronExpression) -> List[LintWarning]:
    """Info when expression targets the 13th and Friday simultaneously."""
    if expr.day_of_month.raw == "13" and expr.day_of_week.raw in ("5", "fri", "FRI"):
        return [LintWarning(
            code="FRIDAY_13TH",
            message="Expression targets the 13th on a Friday — this is a rare combination.",
            severity="info",
        )]
    return []


_RULES = [
    _check_every_minute,
    _check_midnight_only,
    _check_high_frequency,
    _check_friday_13th_pattern,
]


def lint(expr: CronExpression) -> LintResult:
    """Run all lint rules against a parsed CronExpression."""
    warnings: List[LintWarning] = []
    for rule in _RULES:
        warnings.extend(rule(expr))
    return LintResult(warnings=warnings)
