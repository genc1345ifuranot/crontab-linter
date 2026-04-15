"""Storage and retrieval of named cron expression templates."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import List, Optional

DEFAULT_PATH = os.path.expanduser("~/.crontab_linter_templates.json")


@dataclass
class TemplateEntry:
    name: str
    expression: str
    description: str = ""
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "expression": self.expression,
            "description": self.description,
            "tags": self.tags,
        }

    @staticmethod
    def from_dict(data: dict) -> "TemplateEntry":
        return TemplateEntry(
            name=data["name"],
            expression=data["expression"],
            description=data.get("description", ""),
            tags=data.get("tags", []),
        )


def _load_templates(path: Optional[str] = None) -> List[TemplateEntry]:
    p = path or DEFAULT_PATH
    if not os.path.exists(p):
        return []
    with open(p, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [TemplateEntry.from_dict(d) for d in data]


def _save_templates(entries: List[TemplateEntry], path: Optional[str] = None) -> None:
    p = path or DEFAULT_PATH
    with open(p, "w", encoding="utf-8") as f:
        json.dump([e.to_dict() for e in entries], f, indent=2)


def save_template(
    name: str,
    expression: str,
    description: str = "",
    tags: Optional[List[str]] = None,
    path: Optional[str] = None,
) -> TemplateEntry:
    entries = _load_templates(path)
    entries = [e for e in entries if e.name != name]
    entry = TemplateEntry(name=name, expression=expression, description=description, tags=tags or [])
    entries.append(entry)
    _save_templates(entries, path)
    return entry


def get_template(name: str, path: Optional[str] = None) -> Optional[TemplateEntry]:
    for entry in _load_templates(path):
        if entry.name == name:
            return entry
    return None


def delete_template(name: str, path: Optional[str] = None) -> bool:
    entries = _load_templates(path)
    new_entries = [e for e in entries if e.name != name]
    if len(new_entries) == len(entries):
        return False
    _save_templates(new_entries, path)
    return True


def list_templates(path: Optional[str] = None) -> List[TemplateEntry]:
    return _load_templates(path)
