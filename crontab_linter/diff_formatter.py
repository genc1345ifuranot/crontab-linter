"""Format CronDiff results as plain text or JSON."""

import json
from typing import Dict, Any

from .diff import CronDiff


def format_diff_plain(diff: CronDiff) -> str:
    lines = []
    lines.append(f"  old: {diff.old_expr}")
    lines.append(f"  new: {diff.new_expr}")
    lines.append("")

    if not diff.has_changes:
        lines.append("No differences found — expressions are equivalent.")
        return "\n".join(lines)

    lines.append("Changed fields:")
    for f in diff.changed_fields:
        lines.append(f"  {f.name:>12s}: {f.old_value!r:>10} -> {f.new_value!r}")

    lines.append("")
    lines.append(f"Old schedule: {diff.old_explanation}")
    lines.append(f"New schedule: {diff.new_explanation}")
    return "\n".join(lines)


def format_diff_json(diff: CronDiff) -> str:
    payload: Dict[str, Any] = {
        "old_expr": diff.old_expr,
        "new_expr": diff.new_expr,
        "has_changes": diff.has_changes,
        "fields": [
            {
                "name": f.name,
                "old_value": f.old_value,
                "new_value": f.new_value,
                "changed": f.changed,
            }
            for f in diff.fields
        ],
        "old_explanation": diff.old_explanation,
        "new_explanation": diff.new_explanation,
    }
    return json.dumps(payload, indent=2)


def format_diff(diff: CronDiff, fmt: str = "plain") -> str:
    if fmt == "json":
        return format_diff_json(diff)
    return format_diff_plain(diff)
