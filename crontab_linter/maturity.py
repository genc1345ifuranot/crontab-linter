"""Maturity scoring: assess how 'production-ready' a cron expression is."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List

from crontab_linter.parser import CronExpression
from crontab_linter.validator import validate
from crontab_linter.lint_rules import run_lint
from crontab_linter.complexity import compute_complexity


@dataclass
class MaturityResult:
    expression: str
    score: int          # 0-100
    grade: str          # A/B/C/D/F
    issues: List[str] = field(default_factory=list)
    tips: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "expression": self.expression,
            "score": self.score,
            "grade": self.grade,
            "issues": self.issues,
            "tips": self.tips,
        }


def _grade(score: int) -> str:
    if score >= 90:
        return "A"
    if score >= 75:
        return "B"
    if score >= 60:
        return "C"
    if score >= 40:
        return "D"
    return "F"


def assess_maturity(expr: str) -> MaturityResult:
    """Compute a maturity score for a cron expression."""
    score = 100
    issues: List[str] = []
    tips: List[str] = []

    # Validity check (-40 if invalid)
    validation = validate(expr)
    if not validation.valid:
        for e in validation.errors:
            issues.append(f"Invalid: {e}")
        score -= 40

    # Lint warnings
    try:
        parsed = CronExpression.parse(expr)
        lint = run_lint(parsed)
        for w in lint.warnings:
            if w.severity == "error":
                score -= 15
                issues.append(f"Lint error: {w.message}")
            elif w.severity == "warning":
                score -= 8
                issues.append(f"Lint warning: {w.message}")
            else:
                score -= 2
                tips.append(f"Info: {w.message}")

        # Complexity penalty for overly simple expressions used in production
        cx = compute_complexity(parsed)
        if cx.score == 0:
            tips.append("Expression runs every minute — confirm this is intentional.")
            score -= 5
        elif cx.level == "complex":
            tips.append("Expression is complex; consider adding a comment alias.")
    except Exception:
        pass

    score = max(0, min(100, score))
    return MaturityResult(
        expression=expr,
        score=score,
        grade=_grade(score),
        issues=issues,
        tips=tips,
    )
