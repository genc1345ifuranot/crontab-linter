"""Alias management for crontab expressions.

Allows users to save named aliases for cron expressions and retrieve them later.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Dict, Optional

DEFAULT_ALIAS_FILE = os.path.expanduser("~/.crontab_linter_aliases.json")


@dataclass
class AliasEntry:
    name: str
    expression: str
    description: str = ""

    def to_dict(self) -> dict:
        return {"name": self.name, "expression": self.expression, "description": self.description}

    @staticmethod
    def from_dict(data: dict) -> "AliasEntry":
        return AliasEntry(
            name=data["name"],
            expression=data["expression"],
            description=data.get("description", ""),
        )


def _load_aliases(path: str = DEFAULT_ALIAS_FILE) -> Dict[str, AliasEntry]:
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as fh:
        raw = json.load(fh)
    return {name: AliasEntry.from_dict(entry) for name, entry in raw.items()}


def _save_aliases(aliases: Dict[str, AliasEntry], path: str = DEFAULT_ALIAS_FILE) -> None:
    with open(path, "w", encoding="utf-8") as fh:
        json.dump({name: entry.to_dict() for name, entry in aliases.items()}, fh, indent=2)


def save_alias(name: str, expression: str, description: str = "", path: str = DEFAULT_ALIAS_FILE) -> AliasEntry:
    """Save or overwrite an alias."""
    aliases = _load_aliases(path)
    entry = AliasEntry(name=name, expression=expression, description=description)
    aliases[name] = entry
    _save_aliases(aliases, path)
    return entry


def get_alias(name: str, path: str = DEFAULT_ALIAS_FILE) -> Optional[AliasEntry]:
    """Return the alias entry for *name*, or None if not found."""
    return _load_aliases(path).get(name)


def delete_alias(name: str, path: str = DEFAULT_ALIAS_FILE) -> bool:
    """Delete an alias. Returns True if it existed, False otherwise."""
    aliases = _load_aliases(path)
    if name not in aliases:
        return False
    del aliases[name]
    _save_aliases(aliases, path)
    return True


def list_aliases(path: str = DEFAULT_ALIAS_FILE) -> list[AliasEntry]:
    """Return all saved aliases sorted by name."""
    return sorted(_load_aliases(path).values(), key=lambda e: e.name)


def resolve_alias(name_or_expr: str, path: str = DEFAULT_ALIAS_FILE) -> str:
    """If *name_or_expr* matches a saved alias name, return its expression; otherwise return as-is."""
    entry = get_alias(name_or_expr, path)
    return entry.expression if entry is not None else name_or_expr
