"""Format CompareResult for plain text and JSON output."""
import json
from crontab_linter.compare import CompareResult


def format_compare_plain(result: CompareResult) -> str:
    lines = []
    lines.append(f"A: {result.expr_a}")
    lines.append(f"   Valid: {result.valid_a}")
    if result.errors_a:
        for e in result.errors_a:
            lines.append(f"   Error: {e}")
    else:
        lines.append(f"   Explanation: {result.explanation_a}")
        if result.lint_a.has_warnings():
            for w in result.lint_a.warnings:
                lines.append(f"   [{w.severity.upper()}] {w.message}")

    lines.append(f"B: {result.expr_b}")
    lines.append(f"   Valid: {result.valid_b}")
    if result.errors_b:
        for e in result.errors_b:
            lines.append(f"   Error: {e}")
    else:
        lines.append(f"   Explanation: {result.explanation_b}")
        if result.lint_b.has_warnings():
            for w in result.lint_b.warnings:
                lines.append(f"   [{w.severity.upper()}] {w.message}")

    if result.both_valid():
        if result.has_diff():
            lines.append("Changes:")
            for fd in result.diff.changed_fields():
                lines.append(f"  {fd.field_name}: {fd.value_a!r} -> {fd.value_b!r}")
        else:
            lines.append("No differences found.")
    return "\n".join(lines)


def format_compare_json(result: CompareResult) -> str:
    diff_data = None
    if result.diff is not None:
        diff_data = [
            {"field": fd.field_name, "from": fd.value_a, "to": fd.value_b}
            for fd in result.diff.changed_fields()
        ]
    data = {
        "a": {
            "expression": result.expr_a,
            "valid": result.valid_a,
            "errors": result.errors_a,
            "explanation": result.explanation_a,
            "lint": [w.to_dict() for w in result.lint_a.warnings],
        },
        "b": {
            "expression": result.expr_b,
            "valid": result.valid_b,
            "errors": result.errors_b,
            "explanation": result.explanation_b,
            "lint": [w.to_dict() for w in result.lint_b.warnings],
        },
        "diff": diff_data,
    }
    return json.dumps(data, indent=2)


def format_compare(result: CompareResult, fmt: str = "plain") -> str:
    if fmt == "json":
        return format_compare_json(result)
    return format_compare_plain(result)
