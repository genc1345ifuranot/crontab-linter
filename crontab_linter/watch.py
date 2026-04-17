"""Watch a crontab file for changes and re-lint on save."""
from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional

from crontab_linter.batch import process_lines, BatchResult


@dataclass
class WatchEvent:
    path: str
    changed: bool
    result: Optional[BatchResult]
    error: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "path": self.path,
            "changed": self.changed,
            "result": (
                [{"expression": e.expression, "valid": e.is_valid, "errors": e.errors}
                 for e in self.result.entries]
                if self.result else None
            ),
            "error": self.error,
        }


def _file_hash(path: Path) -> str:
    try:
        return hashlib.md5(path.read_bytes()).hexdigest()
    except OSError:
        return ""


def _lint_file(path: Path) -> BatchResult:
    lines = path.read_text().splitlines()
    return process_lines(lines)


def watch(
    filepath: str,
    callback: Callable[[WatchEvent], None],
    interval: float = 1.0,
    max_iterations: Optional[int] = None,
) -> None:
    """Poll *filepath* every *interval* seconds; call *callback* on change."""
    path = Path(filepath)
    last_hash = ""
    iterations = 0

    while True:
        current_hash = _file_hash(path)
        changed = current_hash != last_hash and current_hash != ""

        if changed:
            last_hash = current_hash
            try:
                result = _lint_file(path)
                callback(WatchEvent(path=filepath, changed=True, result=result))
            except Exception as exc:  # noqa: BLE001
                callback(WatchEvent(path=filepath, changed=True, result=None, error=str(exc)))

        iterations += 1
        if max_iterations is not None and iterations >= max_iterations:
            break

        time.sleep(interval)
