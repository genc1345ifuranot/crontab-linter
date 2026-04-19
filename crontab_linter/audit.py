"""Audit log: record every lint/validate action with timestamp and result summary."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional

DEFAULT_AUDIT_FILE = os.path.join(
    os.path.expanduser("~"), ".crontab_linter", "audit.json"
)

MAX_AUDIT_ENTRIES = 500


@dataclass
class AuditEntry:
    """A single audit log record."""

    timestamp: str
    expression: str
    action: str          # e.g. "lint", "validate", "schedule", "diff"
    valid: Optional[bool]
    warnings: int
    errors: List[str] = field(default_factory=list)
    note: str = ""

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "expression": self.expression,
            "action": self.action,
            "valid": self.valid,
            "warnings": self.warnings,
            "errors": self.errors,
            "note": self.note,
        }

    @staticmethod
    def from_dict(d: dict) -> "AuditEntry":
        return AuditEntry(
            timestamp=d["timestamp"],
            expression=d["expression"],
            action=d["action"],
            valid=d.get("valid"),
            warnings=d.get("warnings", 0),
            errors=d.get("errors", []),
            note=d.get("note", ""),
        )


def _load(path: str) -> List[AuditEntry]:
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as fh:
        raw = json.load(fh)
    return [AuditEntry.from_dict(r) for r in raw]


def _save(entries: List[AuditEntry], path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump([e.to_dict() for e in entries], fh, indent=2)


def record(
    expression: str,
    action: str,
    valid: Optional[bool] = None,
    warnings: int = 0,
    errors: Optional[List[str]] = None,
    note: str = "",
    path: str = DEFAULT_AUDIT_FILE,
) -> AuditEntry:
    """Append a new audit entry and persist to disk."""
    entry = AuditEntry(
        timestamp=datetime.now(timezone.utc).isoformat(),
        expression=expression,
        action=action,
        valid=valid,
        warnings=warnings,
        errors=errors or [],
        note=note,
    )
    entries = _load(path)
    entries.append(entry)
    # Keep only the most recent MAX_AUDIT_ENTRIES records
    if len(entries) > MAX_AUDIT_ENTRIES:
        entries = entries[-MAX_AUDIT_ENTRIES:]
    _save(entries, path)
    return entry


def get_all(path: str = DEFAULT_AUDIT_FILE) -> List[AuditEntry]:
    """Return all audit entries, oldest first."""
    return _load(path)


def clear(path: str = DEFAULT_AUDIT_FILE) -> None:
    """Remove all audit log entries."""
    _save([], path)
