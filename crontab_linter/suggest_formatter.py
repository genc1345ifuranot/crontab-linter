"""Format SuggestResult for plain and JSON output."""
from __future__ import annotations
import json
from .suggest import SuggestResult


def format_suggest_plain(result: SuggestResult) -> str:
    lines = [f"Expression : {result.expression}"]
    if not result.has_suggestions:
        lines.append("No suggestions — expression appears valid.")
        return "\n".join(lines)
    lines.append("Suggestions:")
    for s in result.suggestions:
        lines.append(f"  [{s.original}] -> [{s.fixed}]  # {s.reason}")
    fixed_expr = result.expression
    parts = fixed_expr.split()
    if len(parts) == 5:
        for s in result.suggestions:
            parts = [s.fixed if p == s.original else p for p in parts]
        lines.append(f"Suggested fix: {' '.join(parts)}")
    return "\n".join(lines)


def format_suggest_json(result: SuggestResult) -> str:
    data = {
        "expression": result.expression,
        "has_suggestions": result.has_suggestions,
        "suggestions": [
            {"original": s.original, "fixed": s.fixed, "reason": s.reason}
            for s in result.suggestions
        ],
    }
    return json.dumps(data, indent=2)


def format_suggest(result: SuggestResult, fmt: str = "plain") -> str:
    if fmt == "json":
        return format_suggest_json(result)
    return format_suggest_plain(result)
