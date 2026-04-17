"""Annotation support: attach notes to cron expressions stored in a file."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional

DEFAULT_ANNOTATE_FILE = os.path.expanduser("~/.crontab_linter_annotations.json")


@dataclass
class AnnotationEntry:
    expression: str
    notes: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {"expression": self.expression, "notes": self.notes}

    @staticmethod
    def from_dict(d: dict) -> "AnnotationEntry":
        return AnnotationEntry(expression=d["expression"], notes=list(d.get("notes", [])))


def _load(path: str) -> Dict[str, AnnotationEntry]:
    if not os.path.exists(path):
        return {}
    with open(path) as f:
        raw = json.load(f)
    return {k: AnnotationEntry.from_dict(v) for k, v in raw.items()}


def _save(data: Dict[str, AnnotationEntry], path: str) -> None:
    with open(path, "w") as f:
        json.dump({k: v.to_dict() for k, v in data.items()}, f, indent=2)


def add_note(expression: str, note: str, path: str = DEFAULT_ANNOTATE_FILE) -> AnnotationEntry:
    data = _load(path)
    entry = data.get(expression, AnnotationEntry(expression=expression))
    if note not in entry.notes:
        entry.notes.append(note)
    data[expression] = entry
    _save(data, path)
    return entry


def get_notes(expression: str, path: str = DEFAULT_ANNOTATE_FILE) -> Optional[AnnotationEntry]:
    return _load(path).get(expression)


def remove_note(expression: str, note: str, path: str = DEFAULT_ANNOTATE_FILE) -> AnnotationEntry:
    data = _load(path)
    entry = data.get(expression, AnnotationEntry(expression=expression))
    entry.notes = [n for n in entry.notes if n != note]
    data[expression] = entry
    _save(data, path)
    return entry


def list_annotations(path: str = DEFAULT_ANNOTATE_FILE) -> List[AnnotationEntry]:
    return list(_load(path).values())
