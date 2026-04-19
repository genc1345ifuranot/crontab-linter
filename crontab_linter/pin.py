"""Pin/unpin cron expressions for quick reference."""
from __future__ import annotations
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

DEFAULT_PIN_FILE = Path.home() / ".crontab_linter_pins.json"


@dataclass
class PinEntry:
    expression: str
    label: Optional[str] = None
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {"expression": self.expression, "label": self.label, "tags": self.tags}

    @staticmethod
    def from_dict(d: dict) -> "PinEntry":
        return PinEntry(
            expression=d["expression"],
            label=d.get("label"),
            tags=d.get("tags", []),
        )


def _load(path: Path) -> List[PinEntry]:
    if not path.exists():
        return []
    with path.open() as f:
        return [PinEntry.from_dict(e) for e in json.load(f)]


def _save(entries: List[PinEntry], path: Path) -> None:
    with path.open("w") as f:
        json.dump([e.to_dict() for e in entries], f, indent=2)


def pin(expression: str, label: Optional[str] = None, tags: Optional[List[str]] = None,
        path: Path = DEFAULT_PIN_FILE) -> PinEntry:
    entries = _load(path)
    for e in entries:
        if e.expression == expression:
            e.label = label if label is not None else e.label
            if tags:
                e.tags = list(dict.fromkeys(e.tags + tags))
            _save(entries, path)
            return e
    entry = PinEntry(expression=expression, label=label, tags=tags or [])
    entries.append(entry)
    _save(entries, path)
    return entry


def unpin(expression: str, path: Path = DEFAULT_PIN_FILE) -> bool:
    entries = _load(path)
    new = [e for e in entries if e.expression != expression]
    if len(new) == len(entries):
        return False
    _save(new, path)
    return True


def list_pins(path: Path = DEFAULT_PIN_FILE) -> List[PinEntry]:
    return _load(path)


def get_pin(expression: str, path: Path = DEFAULT_PIN_FILE) -> Optional[PinEntry]:
    for e in _load(path):
        if e.expression == expression:
            return e
    return None
