"""Export crontab entries (aliases, tags, snapshots) to various formats."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

from crontab_linter.alias import _load_aliases
from crontab_linter.tags import _load_tags
from crontab_linter.snapshot import _load_snapshots


@dataclass
class ExportResult:
    aliases: list[dict[str, Any]] = field(default_factory=list)
    tags: list[dict[str, Any]] = field(default_factory=list)
    snapshots: list[dict[str, Any]] = field(default_factory=list)

    def total(self) -> int:
        return len(self.aliases) + len(self.tags) + len(self.snapshots)

    def to_dict(self) -> dict[str, Any]:
        return {
            "aliases": self.aliases,
            "tags": self.tags,
            "snapshots": self.snapshots,
            "total": self.total(),
        }


def export_all(
    alias_file: str | None = None,
    tag_file: str | None = None,
    snap_file: str | None = None,
) -> ExportResult:
    kwargs_a = {"path": alias_file} if alias_file else {}
    kwargs_t = {"path": tag_file} if tag_file else {}
    kwargs_s = {"path": snap_file} if snap_file else {}

    aliases = [e.to_dict() for e in _load_aliases(**kwargs_a)]
    tags = [e.to_dict() for e in _load_tags(**kwargs_t)]
    snapshots = [e.to_dict() for e in _load_snapshots(**kwargs_s)]

    return ExportResult(aliases=aliases, tags=tags, snapshots=snapshots)


def format_export_json(result: ExportResult) -> str:
    return json.dumps(result.to_dict(), indent=2)


def format_export_plain(result: ExportResult) -> str:
    lines: list[str] = []
    if result.aliases:
        lines.append(f"Aliases ({len(result.aliases)}):")
        for a in result.aliases:
            lines.append(f"  {a['name']}: {a['expression']}")
    if result.tags:
        lines.append(f"Tags ({len(result.tags)}):")
        for t in result.tags:
            tags_str = ", ".join(t.get("tags", []))
            lines.append(f"  {t['expression']} [{tags_str}]")
    if result.snapshots:
        lines.append(f"Snapshots ({len(result.snapshots)}):")
        for s in result.snapshots:
            lines.append(f"  {s['name']}: {s['expression']}")
    if not lines:
        lines.append("No data to export.")
    return "\n".join(lines)


def format_export(result: ExportResult, fmt: str = "plain") -> str:
    if fmt == "json":
        return format_export_json(result)
    return format_export_plain(result)
