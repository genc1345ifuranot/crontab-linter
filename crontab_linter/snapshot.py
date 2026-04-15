"""Snapshot feature: save and compare cron expression snapshots."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional

DEFAULT_SNAPSHOT_FILE = os.path.expanduser("~/.crontab_linter_snapshots.json")


@dataclass
class SnapshotEntry:
    name: str
    expression: str
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    note: str = ""

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "expression": self.expression,
            "created_at": self.created_at,
            "note": self.note,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "SnapshotEntry":
        return cls(
            name=data["name"],
            expression=data["expression"],
            created_at=data.get("created_at", ""),
            note=data.get("note", ""),
        )


def _load_snapshots(path: str) -> List[SnapshotEntry]:
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as fh:
        raw = json.load(fh)
    return [SnapshotEntry.from_dict(d) for d in raw]


def _save_snapshots(entries: List[SnapshotEntry], path: str) -> None:
    with open(path, "w", encoding="utf-8") as fh:
        json.dump([e.to_dict() for e in entries], fh, indent=2)


def save_snapshot(name: str, expression: str, note: str = "",
                  path: str = DEFAULT_SNAPSHOT_FILE) -> SnapshotEntry:
    entries = _load_snapshots(path)
    entries = [e for e in entries if e.name != name]
    entry = SnapshotEntry(name=name, expression=expression, note=note)
    entries.append(entry)
    _save_snapshots(entries, path)
    return entry


def get_snapshot(name: str, path: str = DEFAULT_SNAPSHOT_FILE) -> Optional[SnapshotEntry]:
    for e in _load_snapshots(path):
        if e.name == name:
            return e
    return None


def delete_snapshot(name: str, path: str = DEFAULT_SNAPSHOT_FILE) -> bool:
    entries = _load_snapshots(path)
    new_entries = [e for e in entries if e.name != name]
    if len(new_entries) == len(entries):
        return False
    _save_snapshots(new_entries, path)
    return True


def list_snapshots(path: str = DEFAULT_SNAPSHOT_FILE) -> List[SnapshotEntry]:
    return _load_snapshots(path)
