"""Tests for crontab_linter.history module."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from crontab_linter.history import (
    HistoryEntry,
    _MAX_ENTRIES,
    clear_history,
    get_history,
    record_entry,
)


@pytest.fixture()
def tmp_history(tmp_path: Path) -> Path:
    return tmp_path / "history.json"


def _make_entry(expr: str = "* * * * *", valid: bool = True) -> HistoryEntry:
    return HistoryEntry(
        expression=expr,
        timezone="UTC",
        valid=valid,
        errors=[] if valid else ["some error"],
        warnings=[],
        explanation="Every minute",
    )


def test_record_and_retrieve(tmp_history: Path) -> None:
    entry = _make_entry()
    record_entry(entry, path=tmp_history)
    history = get_history(path=tmp_history)
    assert len(history) == 1
    assert history[0].expression == "* * * * *"
    assert history[0].valid is True


def test_multiple_entries_ordered(tmp_history: Path) -> None:
    for expr in ["0 * * * *", "0 0 * * *", "0 0 1 * *"]:
        record_entry(_make_entry(expr), path=tmp_history)
    history = get_history(path=tmp_history)
    assert [e.expression for e in history] == ["0 * * * *", "0 0 * * *", "0 0 1 * *"]


def test_cap_at_max_entries(tmp_history: Path) -> None:
    for i in range(_MAX_ENTRIES + 10):
        record_entry(_make_entry(str(i)), path=tmp_history)
    history = get_history(path=tmp_history)
    assert len(history) == _MAX_ENTRIES
    # Oldest entries should have been dropped
    assert history[0].expression == "10"


def test_clear_history(tmp_history: Path) -> None:
    record_entry(_make_entry(), path=tmp_history)
    removed = clear_history(path=tmp_history)
    assert removed == 1
    assert get_history(path=tmp_history) == []


def test_clear_nonexistent_history(tmp_history: Path) -> None:
    removed = clear_history(path=tmp_history)
    assert removed == 0


def test_get_history_missing_file(tmp_history: Path) -> None:
    assert get_history(path=tmp_history) == []


def test_get_history_corrupt_file(tmp_history: Path) -> None:
    tmp_history.write_text("not valid json", encoding="utf-8")
    assert get_history(path=tmp_history) == []


def test_entry_roundtrip() -> None:
    entry = _make_entry(valid=False)
    data = entry.to_dict()
    restored = HistoryEntry.from_dict(data)
    assert restored.expression == entry.expression
    assert restored.valid == entry.valid
    assert restored.errors == entry.errors
    assert restored.timestamp == entry.timestamp


def test_history_file_is_valid_json(tmp_history: Path) -> None:
    record_entry(_make_entry(), path=tmp_history)
    raw = json.loads(tmp_history.read_text(encoding="utf-8"))
    assert isinstance(raw, list)
    assert raw[0]["expression"] == "* * * * *"
