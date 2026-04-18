"""Rename an alias or template in-place."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Literal

from crontab_linter.alias import _load_aliases, _save_aliases
from crontab_linter.template import _load_templates, _save_templates

Kind = Literal["alias", "template"]


@dataclass
class RenameResult:
    kind: Kind
    old_name: str
    new_name: str
    ok: bool
    error: str = ""

    def to_dict(self) -> dict:
        return {
            "kind": self.kind,
            "old_name": self.old_name,
            "new_name": self.new_name,
            "ok": self.ok,
            "error": self.error,
        }


def rename(kind: Kind, old_name: str, new_name: str, store_path: str | None = None) -> RenameResult:
    if kind == "alias":
        entries = _load_aliases(store_path)
        if old_name not in entries:
            return RenameResult(kind, old_name, new_name, False, f"alias '{old_name}' not found")
        if new_name in entries:
            return RenameResult(kind, old_name, new_name, False, f"alias '{new_name}' already exists")
        entries[new_name] = entries.pop(old_name)
        entries[new_name].name = new_name
        _save_aliases(entries, store_path)
    elif kind == "template":
        entries = _load_templates(store_path)
        if old_name not in entries:
            return RenameResult(kind, old_name, new_name, False, f"template '{old_name}' not found")
        if new_name in entries:
            return RenameResult(kind, old_name, new_name, False, f"template '{new_name}' already exists")
        entries[new_name] = entries.pop(old_name)
        entries[new_name].name = new_name
        _save_templates(entries, store_path)
    else:
        return RenameResult(kind, old_name, new_name, False, f"unknown kind '{kind}'")
    return RenameResult(kind, old_name, new_name, True)
