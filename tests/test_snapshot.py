"""Tests for snapshot save/get/delete/list and compare CLI commands."""
from __future__ import annotations

import argparse
import json
import os
import pytest

from crontab_linter.snapshot import (
    delete_snapshot,
    get_snapshot,
    list_snapshots,
    save_snapshot,
)
from crontab_linter.snapshot_cli import (
    cmd_compare,
    cmd_delete,
    cmd_get,
    cmd_list,
    cmd_save,
)


@pytest.fixture()
def snap_file(tmp_path):
    return str(tmp_path / "snapshots.json")


def _ns(**kwargs):
    defaults = {"snapshot_file": None, "note": ""}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


# --- unit tests for snapshot module ---

def test_save_and_get(snap_file):
    entry = save_snapshot("daily", "0 0 * * *", path=snap_file)
    assert entry.name == "daily"
    assert entry.expression == "0 0 * * *"
    result = get_snapshot("daily", path=snap_file)
    assert result is not None
    assert result.expression == "0 0 * * *"


def test_get_missing_returns_none(snap_file):
    assert get_snapshot("nonexistent", path=snap_file) is None


def test_overwrite_existing(snap_file):
    save_snapshot("job", "0 0 * * *", path=snap_file)
    save_snapshot("job", "0 6 * * *", path=snap_file)
    entries = list_snapshots(path=snap_file)
    assert len(entries) == 1
    assert entries[0].expression == "0 6 * * *"


def test_delete_snapshot(snap_file):
    save_snapshot("tmp", "* * * * *", path=snap_file)
    removed = delete_snapshot("tmp", path=snap_file)
    assert removed is True
    assert get_snapshot("tmp", path=snap_file) is None


def test_delete_missing_returns_false(snap_file):
    assert delete_snapshot("ghost", path=snap_file) is False


def test_list_snapshots(snap_file):
    save_snapshot("a", "0 0 * * *", path=snap_file)
    save_snapshot("b", "0 6 * * *", path=snap_file)
    entries = list_snapshots(path=snap_file)
    names = [e.name for e in entries]
    assert "a" in names and "b" in names


def test_note_persisted(snap_file):
    save_snapshot("noted", "0 0 * * *", note="runs at midnight", path=snap_file)
    e = get_snapshot("noted", path=snap_file)
    assert e.note == "runs at midnight"


# --- CLI command tests ---

def test_cmd_save_valid(snap_file, capsys):
    cmd_save(_ns(name="nightly", expression="0 0 * * *", snapshot_file=snap_file))
    out = capsys.readouterr().out
    assert "nightly" in out


def test_cmd_save_invalid_expression_exits(snap_file):
    with pytest.raises(SystemExit):
        cmd_save(_ns(name="bad", expression="99 99 99 99 99", snapshot_file=snap_file))


def test_cmd_get_missing_exits(snap_file):
    with pytest.raises(SystemExit):
        cmd_get(_ns(name="missing", snapshot_file=snap_file))


def test_cmd_list_empty(snap_file, capsys):
    cmd_list(_ns(snapshot_file=snap_file))
    assert "No snapshots" in capsys.readouterr().out


def test_cmd_delete_existing(snap_file, capsys):
    save_snapshot("del_me", "0 0 * * *", path=snap_file)
    cmd_delete(_ns(name="del_me", snapshot_file=snap_file))
    assert "deleted" in capsys.readouterr().out


def test_cmd_compare_shows_diff(snap_file, capsys):
    save_snapshot("base", "0 0 * * *", path=snap_file)
    cmd_compare(_ns(name="base", expression="0 6 * * *",
                    format="plain", snapshot_file=snap_file))
    out = capsys.readouterr().out
    assert len(out) > 0


def test_cmd_compare_missing_snapshot_exits(snap_file):
    with pytest.raises(SystemExit):
        cmd_compare(_ns(name="nope", expression="0 0 * * *",
                        format="plain", snapshot_file=snap_file))
