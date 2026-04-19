import json
from crontab_linter.duplicate import DuplicateResult


def format_duplicate_plain(result: DuplicateResult) -> str:
    if not result.has_duplicates():
        return "No duplicate expressions found."

    lines = [f"Found {len(result.groups)} duplicate group(s):"]
    for g in result.groups:
        lines.append(f"  Expression: {g.expression}")
        lines.append(f"  Used by ({g.count()}): {', '.join(g.sources)}")
        lines.append("")
    lines.append(f"Total redundant entries: {result.total_duplicates()}")
    return "\n".join(lines)


def format_duplicate_json(result: DuplicateResult) -> str:
    return json.dumps(result.to_dict(), indent=2)


def format_duplicate(result: DuplicateResult, fmt: str = "plain") -> str:
    if fmt == "json":
        return format_duplicate_json(result)
    return format_duplicate_plain(result)
