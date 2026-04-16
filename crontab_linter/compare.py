"""Compare two crontab expressions and summarize differences with explanations."""
from dataclasses import dataclass, field
from typing import List, Optional

from crontab_linter.parser import CronExpression, parse
from crontab_linter.validator import validate, ValidationResult
from crontab_linter.explainer import explain
from crontab_linter.diff import diff_expressions, CronDiff
from crontab_linter.lint_rules import lint, LintResult


@dataclass
class CompareResult:
    expr_a: str
    expr_b: str
    valid_a: bool
    valid_b: bool
    errors_a: List[str]
    errors_b: List[str]
    explanation_a: str
    explanation_b: str
    diff: Optional[CronDiff]
    lint_a: LintResult
    lint_b: LintResult

    def has_diff(self) -> bool:
        return self.diff is not None and self.diff.has_changes()

    def both_valid(self) -> bool:
        return self.valid_a and self.valid_b


def compare(expr_a: str, expr_b: str) -> CompareResult:
    """Compare two cron expression strings and return a CompareResult."""
    try:
        parsed_a = parse(expr_a)
        val_a = validate(parsed_a)
        exp_a = explain(parsed_a)
        lint_a = lint(parsed_a)
    except Exception as e:
        return CompareResult(
            expr_a=expr_a, expr_b=expr_b,
            valid_a=False, valid_b=False,
            errors_a=[str(e)], errors_b=[],
            explanation_a="", explanation_b="",
            diff=None,
            lint_a=LintResult(warnings=[]),
            lint_b=LintResult(warnings=[]),
        )

    try:
        parsed_b = parse(expr_b)
        val_b = validate(parsed_b)
        exp_b = explain(parsed_b)
        lint_b = lint(parsed_b)
    except Exception as e:
        return CompareResult(
            expr_a=expr_a, expr_b=expr_b,
            valid_a=val_a.valid, valid_b=False,
            errors_a=val_a.errors, errors_b=[str(e)],
            explanation_a=exp_a, explanation_b="",
            diff=None,
            lint_a=lint_a,
            lint_b=LintResult(warnings=[]),
        )

    diff = diff_expressions(parsed_a, parsed_b) if val_a.valid and val_b.valid else None

    return CompareResult(
        expr_a=expr_a, expr_b=expr_b,
        valid_a=val_a.valid, valid_b=val_b.valid,
        errors_a=val_a.errors, errors_b=val_b.errors,
        explanation_a=exp_a, explanation_b=exp_b,
        diff=diff,
        lint_a=lint_a,
        lint_b=lint_b,
    )
