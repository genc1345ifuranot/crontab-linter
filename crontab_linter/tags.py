"""Tag management for crontab expressions — save, list, and filter by tag."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional

_DEFAULT_TAGS_FILE = os.path.expanduser("~/.crontab_linter_tags.json")


@dataclass
class TagEntry:
    expression: str
    tags: List[str]
    note: str = ""

    def to_dict(self) -> dict:
        return {"expression": self.expression, "tags": self.tags, "note": self.note}

    @staticmethod
    def from_dict(d: dict) -> "TagEntry":
        return TagEntry(
            expression=d["expression"],
            tags=d.get("tags", []),
            note=d.get("note", ""),
        )


def _load_tags(path: str = _DEFAULT_TAGS_FILE) -> List[TagEntry]:
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as fh:
        raw = json.load(fh)
    return [TagEntry.from_dict(item) for item in raw]


def _save_tags(entries: List[TagEntry], path: str = _DEFAULT_TAGS_FILE) -> None:
    with open(path, "w", encoding="utf-8") as fh:
        json.dump([e.to_dict() for e in entries], fh, indent=2)


def tag_expression(
    expression: str,
    tags: List[str],
    note: str = "",
    path: str = _DEFAULT_TAGS_FILE,
) -> TagEntry:
    """Add or update tags for a crontab expression."""
    entries = _load_tags(path)
    for entry in entries:
        if entry.expression == expression:
            entry.tags = sorted(set(entry.tags) | set(tags))
            if note:
                entry.note = note
            _save_tags(entries, path)
            return entry
    new_entry = TagEntry(expression=expression, tags=sorted(set(tags)), note=note)
    entries.append(new_entry)
    _save_tags(entries, path)
    return new_entry


def get_by_tag(tag: str, path: str = _DEFAULT_TAGS_FILE) -> List[TagEntry]:
    """Return all entries that have the given tag."""
    return [e for e in _load_tags(path) if tag in e.tags]


def list_tags(path: str = _DEFAULT_TAGS_FILE) -> List[TagEntry]:
    """Return all tagged entries."""
    return _load_tags(path)


def remove_tag(
    expression: str, tag: str, path: str = _DEFAULT_TAGS_FILE
) -> Optional[TagEntry]:
    """Remove a single tag from an expression. Returns updated entry or None."""
    entries = _load_tags(path)
    for entry in entries:
        if entry.expression == expression:
            entry.tags = [t for t in entry.tags if t != tag]
            _save_tags(entries, path)
            return entry
    return None
