"""Tests for crontab_linter.history_cli sub-commands."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from unittest.mock import patch

import pytest

from crontab_linter.history import HistoryEntry, record_entry
from crontab_linter.history_cli import cmd_clear, cmd_export, cmd_list


@pytest.fixture()
def tmp_history(tmp_path: Path) -> Path:
    return tmp_path / "history.json"


def _make_entry(expr: str = "*/5 * * * *", valid: bool = True) -> HistoryEntry:
    return HistoryEntry(
        expression=expr,
        timezone="America/New_York",
        valid=valid,
        errors=[],
        warnings=["DST warning"] if valid else [],
        explanation="Every 5 minutes",
    )


def _ns(**kwargs) -> argparse.Namespace:
    return argparse.Namespace(**kwargs)


def test_cmd_list_empty(tmp_history: Path, capsys) -> None:
    with patch("crontab_linter.history_cli.get_history", return_value=[]):
        code = cmd_list(_ns(limit=20))
    assert code == 0
    captured = capsys.readouterr()
    assert "No history" in captured.out


def test_cmd_list_shows_entries(tmp_history: Path, capsys) -> None:
    entries = [_make_entry("0 * * * *"), _make_entry("0 0 * * *", valid=False)]
    with patch("crontab_linter.history_cli.get_history", return_value=entries):
        code = cmd_list(_ns(limit=20))
    assert code == 0
    out = capsys.readouterr().out
    assert "0 * * * *" in out
    assert "0 0 * * *" in out
    assert "valid" in out


def test_cmd_list_respects_limit(capsys) -> None:
    entries = [_make_entry(str(i)) for i in range(10)]
    with patch("crontab_linter.history_cli.get_history", return_value=entries):
        cmd_list(_ns(limit=3))
    out = capsys.readouterr().out
    # Only last 3 entries should appear
    assert "7" in out
    assert "0" not in out


def test_cmd_clear(capsys) -> None:
    with patch("crontab_linter.history_cli.clear_history", return_value=5):
        code = cmd_clear(_ns())
    assert code == 0
    assert "5" in capsys.readouterr().out


def test_cmd_export_stdout(capsys) -> None:
    entries = [_make_entry()]
    with patch("crontab_linter.history_cli.get_history", return_value=entries):
        code = cmd_export(_ns(output=""))
    assert code == 0
    out = capsys.readouterr().out
    data = json.loads(out)
    assert data[0]["expression"] == "*/5 * * * *"


def test_cmd_export_to_file(tmp_path: Path, capsys) -> None:
    out_file = tmp_path / "out.json"
    entries = [_make_entry()]
    with patch("crontab_linter.history_cli.get_history", return_value=entries):
        code = cmd_export(_ns(output=str(out_file)))
    assert code == 0
    assert out_file.exists()
    data = json.loads(out_file.read_text())
    assert len(data) == 1
