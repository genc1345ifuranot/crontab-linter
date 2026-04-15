"""Tests for crontab_linter.alias and crontab_linter.alias_cli."""
from __future__ import annotations

import argparse
import json
import os

import pytest

from crontab_linter.alias import (
    delete_alias,
    get_alias,
    list_aliases,
    resolve_alias,
    save_alias,
)
from crontab_linter.alias_cli import cmd_delete, cmd_get, cmd_list, cmd_save


@pytest.fixture()
def alias_file(tmp_path):
    return str(tmp_path / "aliases.json")


def _ns(**kwargs):
    defaults = {"alias_file": None, "json": False, "description": ""}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


# --- alias module ---

def test_save_and_get(alias_file):
    entry = save_alias("daily", "0 0 * * *", path=alias_file)
    assert entry.name == "daily"
    assert entry.expression == "0 0 * * *"
    result = get_alias("daily", path=alias_file)
    assert result is not None
    assert result.expression == "0 0 * * *"


def test_get_missing_returns_none(alias_file):
    assert get_alias("nonexistent", path=alias_file) is None


def test_overwrite_alias(alias_file):
    save_alias("job", "*/5 * * * *", path=alias_file)
    save_alias("job", "0 12 * * *", path=alias_file)
    assert get_alias("job", path=alias_file).expression == "0 12 * * *"


def test_delete_existing(alias_file):
    save_alias("tmp", "* * * * *", path=alias_file)
    assert delete_alias("tmp", path=alias_file) is True
    assert get_alias("tmp", path=alias_file) is None


def test_delete_missing_returns_false(alias_file):
    assert delete_alias("ghost", path=alias_file) is False


def test_list_aliases_sorted(alias_file):
    save_alias("zebra", "* * * * *", path=alias_file)
    save_alias("alpha", "0 0 * * *", path=alias_file)
    names = [e.name for e in list_aliases(path=alias_file)]
    assert names == sorted(names)


def test_list_aliases_empty(alias_file):
    assert list_aliases(path=alias_file) == []


def test_resolve_alias_known(alias_file):
    save_alias("weekly", "0 0 * * 0", path=alias_file)
    assert resolve_alias("weekly", path=alias_file) == "0 0 * * 0"


def test_resolve_alias_unknown_passthrough(alias_file):
    assert resolve_alias("0 6 * * 1", path=alias_file) == "0 6 * * 1"


def test_alias_with_description(alias_file):
    save_alias("nightly", "0 2 * * *", description="Runs at 2am", path=alias_file)
    entry = get_alias("nightly", path=alias_file)
    assert entry.description == "Runs at 2am"


# --- alias_cli ---

def test_cmd_save_prints(alias_file, capsys):
    cmd_save(_ns(alias_file=alias_file, name="myjob", expression="*/10 * * * *", description=""))
    out = capsys.readouterr().out
    assert "myjob" in out
    assert "*/10 * * * *" in out


def test_cmd_get_missing_exits(alias_file):
    with pytest.raises(SystemExit):
        cmd_get(_ns(alias_file=alias_file, name="missing"))


def test_cmd_list_json(alias_file, capsys):
    save_alias("a", "* * * * *", path=alias_file)
    cmd_list(_ns(alias_file=alias_file, json=True))
    data = json.loads(capsys.readouterr().out)
    assert isinstance(data, list)
    assert data[0]["name"] == "a"


def test_cmd_delete_missing_exits(alias_file):
    with pytest.raises(SystemExit):
        cmd_delete(_ns(alias_file=alias_file, name="nope"))
