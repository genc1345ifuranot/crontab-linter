"""Search/filter saved aliases, tags, and snapshots by expression or metadata."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from crontab_linter.alias import _load_aliases, AliasEntry
from crontab_linter.tags import _load_tags, TagEntry
from crontab_linter.snapshot import _load_snapshots, SnapshotEntry


@dataclass
class SearchResult:
    aliases: List[AliasEntry] = field(default_factory=list)
    tags: List[TagEntry] = field(default_factory=list)
    snapshots: List[SnapshotEntry] = field(default_factory=list)

    @property
    def total(self) -> int:
        return len(self.aliases) + len(self.tags) + len(self.snapshots)

    def is_empty(self) -> bool:
        return self.total == 0


def _match(text: str, query: str) -> bool:
    """Case-insensitive substring match."""
    return query.lower() in text.lower()


def search(
    query: str,
    *,
    alias_file: Optional[str] = None,
    tag_file: Optional[str] = None,
    snapshot_file: Optional[str] = None,
    search_aliases: bool = True,
    search_tags: bool = True,
    search_snapshots: bool = True,
) -> SearchResult:
    """Search across stored aliases, tags, and snapshots for *query*."""
    result = SearchResult()

    if search_aliases:
        kwargs = {"alias_file": alias_file} if alias_file else {}
        for entry in _load_aliases(**kwargs):
            if _match(entry.name, query) or _match(entry.expression, query):
                result.aliases.append(entry)

    if search_tags:
        kwargs = {"tag_file": tag_file} if tag_file else {}
        for entry in _load_tags(**kwargs):
            tag_str = " ".join(entry.tags)
            note_str = entry.note or ""
            if (
                _match(entry.expression, query)
                or _match(tag_str, query)
                or _match(note_str, query)
            ):
                result.tags.append(entry)

    if search_snapshots:
        kwargs = {"snapshot_file": snapshot_file} if snapshot_file else {}
        for entry in _load_snapshots(**kwargs):
            note_str = entry.note or ""
            if _match(entry.name, query) or _match(entry.expression, query) or _match(note_str, query):
                result.snapshots.append(entry)

    return result
