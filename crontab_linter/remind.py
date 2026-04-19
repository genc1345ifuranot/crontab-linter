"""Reminder/note storage keyed by cron expression."""
from __future__ import annotations
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

DEFAULT_PATH = Path.home() / ".crontab_linter_reminders.json"


@dataclass
class ReminderEntry:
    expression: str
    message: str
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {"expression": self.expression, "message": self.message, "tags": self.tags}

    @staticmethod
    def from_dict(d: dict) -> "ReminderEntry":
        return ReminderEntry(d["expression"], d["message"], d.get("tags", []))


def _load(path: Path) -> List[ReminderEntry]:
    if not path.exists():
        return []
    return [ReminderEntry.from_dict(e) for e in json.loads(path.read_text())]


def _save(entries: List[ReminderEntry], path: Path) -> None:
    path.write_text(json.dumps([e.to_dict() for e in entries], indent=2))


def add_reminder(expression: str, message: str, tags: List[str] | None = None, path: Path = DEFAULT_PATH) -> ReminderEntry:
    entries = _load(path)
    entries = [e for e in entries if e.expression != expression]
    entry = ReminderEntry(expression, message, tags or [])
    entries.append(entry)
    _save(entries, path)
    return entry


def get_reminder(expression: str, path: Path = DEFAULT_PATH) -> Optional[ReminderEntry]:
    return next((e for e in _load(path) if e.expression == expression), None)


def remove_reminder(expression: str, path: Path = DEFAULT_PATH) -> bool:
    entries = _load(path)
    new = [e for e in entries if e.expression != expression]
    if len(new) == len(entries):
        return False
    _save(new, path)
    return True


def list_reminders(path: Path = DEFAULT_PATH) -> List[ReminderEntry]:
    return _load(path)
