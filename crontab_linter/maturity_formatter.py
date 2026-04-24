"""Formatters for MaturityResult."""
from __future__ import annotations
import json
from crontab_linter.maturity import MaturityResult


def format_maturity_plain(result: MaturityResult) -> str:
    lines = [
        f"Expression : {result.expression}",
        f"Score      : {result.score}/100",
        f"Grade      : {result.grade}",
    ]
    if result.issues:
        lines.append("Issues:")
        for issue in result.issues:
            lines.append(f"  - {issue}")
    if result.tips:
        lines.append("Tips:")
        for tip in result.tips:
            lines.append(f"  * {tip}")
    if not result.issues and not result.tips:
        lines.append("No issues found.")
    return "\n".join(lines)


def format_maturity_json(result: MaturityResult) -> str:
    return json.dumps(result.to_dict(), indent=2)


def format_maturity(result: MaturityResult, fmt: str = "plain") -> str:
    if fmt == "json":
        return format_maturity_json(result)
    return format_maturity_plain(result)
