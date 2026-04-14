"""Lint history tracking: save and retrieve past linting results."""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

DEFAULT_HISTORY_PATH = Path.home() / ".crontab_linter_history.json"
_MAX_ENTRIES = 100


@dataclass
class HistoryEntry:
    expression: str
    timezone: Optional[str]
    valid: bool
    errors: List[str]
    warnings: List[str]
    explanation: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "HistoryEntry":
        return cls(**data)


def _load_history(path: Path) -> List[HistoryEntry]:
    if not path.exists():
        return []
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        return [HistoryEntry.from_dict(e) for e in raw]
    except (json.JSONDecodeError, TypeError, KeyError):
        return []


def _save_history(entries: List[HistoryEntry], path: Path) -> None:
    path.write_text(
        json.dumps([e.to_dict() for e in entries], indent=2),
        encoding="utf-8",
    )


def record_entry(entry: HistoryEntry, path: Path = DEFAULT_HISTORY_PATH) -> None:
    """Append *entry* to the history file, capping at _MAX_ENTRIES."""
    entries = _load_history(path)
    entries.append(entry)
    if len(entries) > _MAX_ENTRIES:
        entries = entries[-_MAX_ENTRIES:]
    _save_history(entries, path)


def get_history(path: Path = DEFAULT_HISTORY_PATH) -> List[HistoryEntry]:
    """Return all stored history entries (oldest first)."""
    return _load_history(path)


def clear_history(path: Path = DEFAULT_HISTORY_PATH) -> int:
    """Delete all history entries. Returns the number of entries removed."""
    entries = _load_history(path)
    count = len(entries)
    if path.exists():
        path.unlink()
    return count
