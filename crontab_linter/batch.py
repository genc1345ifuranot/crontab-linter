"""Batch validation of multiple crontab expressions from a file or list."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from .parser import CronExpression, parse
from .validator import validate, ValidationResult
from .explainer import explain
from .lint_rules import run_lint, LintResult
from .presets import resolve_preset, is_preset


@dataclass
class BatchEntry:
    line_number: int
    raw: str
    expression: Optional[str]
    comment: Optional[str]
    validation: Optional[ValidationResult]
    lint: Optional[LintResult]
    explanation: Optional[str]
    parse_error: Optional[str]

    def is_valid(self) -> bool:
        return self.parse_error is None and (
            self.validation is not None and self.validation.valid
        )


@dataclass
class BatchResult:
    entries: List[BatchEntry] = field(default_factory=list)

    @property
    def total(self) -> int:
        return len(self.entries)

    @property
    def valid_count(self) -> int:
        return sum(1 for e in self.entries if e.is_valid())

    @property
    def invalid_count(self) -> int:
        return self.total - self.valid_count


def _parse_line(line: str):
    """Strip inline comments and return (expression_str, comment)."""
    if '#' in line:
        idx = line.index('#')
        return line[:idx].strip(), line[idx + 1:].strip()
    return line.strip(), None


def validate_batch(lines: List[str]) -> BatchResult:
    """Validate a list of raw crontab lines."""
    result = BatchResult()
    for lineno, raw in enumerate(lines, start=1):
        stripped = raw.strip()
        if not stripped or stripped.startswith('#'):
            continue

        expr_str, comment = _parse_line(stripped)
        if not expr_str:
            continue

        if is_preset(expr_str):
            expr_str = resolve_preset(expr_str)

        try:
            parsed: CronExpression = parse(expr_str)
            validation = validate(parsed)
            lint = run_lint(parsed)
            explanation = explain(parsed)
            entry = BatchEntry(
                line_number=lineno,
                raw=raw.rstrip(),
                expression=expr_str,
                comment=comment,
                validation=validation,
                lint=lint,
                explanation=explanation,
                parse_error=None,
            )
        except Exception as exc:  # noqa: BLE001
            entry = BatchEntry(
                line_number=lineno,
                raw=raw.rstrip(),
                expression=expr_str,
                comment=comment,
                validation=None,
                lint=None,
                explanation=None,
                parse_error=str(exc),
            )
        result.entries.append(entry)
    return result


def validate_batch_file(path: str) -> BatchResult:
    """Read a file and validate every crontab expression found in it."""
    with open(path, encoding="utf-8") as fh:
        lines = fh.readlines()
    return validate_batch(lines)
