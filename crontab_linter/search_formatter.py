"""Format SearchResult for plain-text and JSON output."""
from __future__ import annotations

import json
from typing import Literal

from crontab_linter.search import SearchResult


def format_search_plain(result: SearchResult, query: str) -> str:
    if result.is_empty():
        return f"No results found for '{query}'."

    lines = [f"Search results for '{query}' ({result.total} match(es)):\n"]

    if result.aliases:
        lines.append(f"  Aliases ({len(result.aliases)}):")
        for a in result.aliases:
            lines.append(f"    [{a.name}]  {a.expression}")

    if result.tags:
        lines.append(f"  Tags ({len(result.tags)}):")
        for t in result.tags:
            tag_str = ", ".join(t.tags) if t.tags else "—"
            lines.append(f"    {t.expression}  tags=[{tag_str}]" + (f"  note={t.note}" if t.note else ""))

    if result.snapshots:
        lines.append(f"  Snapshots ({len(result.snapshots)}):")
        for s in result.snapshots:
            lines.append(f"    [{s.name}]  {s.expression}" + (f"  note={s.note}" if s.note else ""))

    return "\n".join(lines)


def format_search_json(result: SearchResult) -> str:
    data = {
        "aliases": [{"name": a.name, "expression": a.expression} for a in result.aliases],
        "tags": [
            {"expression": t.expression, "tags": t.tags, "note": t.note}
            for t in result.tags
        ],
        "snapshots": [
            {"name": s.name, "expression": s.expression, "note": s.note}
            for s in result.snapshots
        ],
        "total": result.total,
    }
    return json.dumps(data, indent=2)


def format_search(
    result: SearchResult,
    query: str,
    fmt: Literal["plain", "json"] = "plain",
) -> str:
    if fmt == "json":
        return format_search_json(result)
    return format_search_plain(result, query)
