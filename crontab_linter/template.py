"""Template management for saving and reusing cron expression templates."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional

DEFAULT_TEMPLATE_FILE = os.path.expanduser("~/.crontab_linter_templates.json")


@dataclass
class TemplateEntry:
    name: str
    expression: str
    description: str = ""
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "expression": self.expression,
            "description": self.description,
            "tags": self.tags,
        }

    @staticmethod
    def from_dict(data: Dict) -> "TemplateEntry":
        return TemplateEntry(
            name=data["name"],
            expression=data["expression"],
            description=data.get("description", ""),
            tags=data.get("tags", []),
        )


def _load_templates(path: str = DEFAULT_TEMPLATE_FILE) -> Dict[str, TemplateEntry]:
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as fh:
        raw = json.load(fh)
    return {k: TemplateEntry.from_dict(v) for k, v in raw.items()}


def _save_templates(templates: Dict[str, TemplateEntry], path: str = DEFAULT_TEMPLATE_FILE) -> None:
    with open(path, "w", encoding="utf-8") as fh:
        json.dump({k: v.to_dict() for k, v in templates.items()}, fh, indent=2)


def save_template(
    name: str,
    expression: str,
    description: str = "",
    tags: Optional[List[str]] = None,
    path: str = DEFAULT_TEMPLATE_FILE,
) -> TemplateEntry:
    templates = _load_templates(path)
    entry = TemplateEntry(name=name, expression=expression, description=description, tags=tags or [])
    templates[name] = entry
    _save_templates(templates, path)
    return entry


def get_template(name: str, path: str = DEFAULT_TEMPLATE_FILE) -> Optional[TemplateEntry]:
    return _load_templates(path).get(name)


def delete_template(name: str, path: str = DEFAULT_TEMPLATE_FILE) -> bool:
    templates = _load_templates(path)
    if name not in templates:
        return False
    del templates[name]
    _save_templates(templates, path)
    return True


def list_templates(path: str = DEFAULT_TEMPLATE_FILE) -> List[TemplateEntry]:
    return list(_load_templates(path).values())
