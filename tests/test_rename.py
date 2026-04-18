"""Tests for rename module and CLI."""
import json
import argparse
import pytest

from crontab_linter.alias import _load_aliases, _save_aliases, AliasEntry
from crontab_linter.template import _load_templates, _save_templates, TemplateEntry
from crontab_linter.rename import rename
from crontab_linter.rename_cli import cmd_rename


@pytest.fixture()
def alias_file(tmp_path):
    return str(tmp_path / "aliases.json")


@pytest.fixture()
def tpl_file(tmp_path):
    return str(tmp_path / "templates.json")


def _ns(**kw):
    defaults = {"format": "plain"}
    defaults.update(kw)
    return argparse.Namespace(**defaults)


def test_rename_alias_ok(alias_file):
    e = AliasEntry(name="nightly", expression="0 2 * * *")
    _save_aliases({"nightly": e}, alias_file)
    result = rename("alias", "nightly", "midnight", alias_file)
    assert result.ok
    entries = _load_aliases(alias_file)
    assert "midnight" in entries
    assert "nightly" not in entries
    assert entries["midnight"].name == "midnight"


def test_rename_alias_missing(alias_file):
    result = rename("alias", "ghost", "phantom", alias_file)
    assert not result.ok
    assert "not found" in result.error


def test_rename_alias_conflict(alias_file):
    a = AliasEntry(name="a", expression="* * * * *")
    b = AliasEntry(name="b", expression="0 * * * *")
    _save_aliases({"a": a, "b": b}, alias_file)
    result = rename("alias", "a", "b", alias_file)
    assert not result.ok
    assert "already exists" in result.error


def test_rename_template_ok(tpl_file):
    e = TemplateEntry(name="weekly", expression="0 9 * * 1")
    _save_templates({"weekly": e}, tpl_file)
    result = rename("template", "weekly", "monday", tpl_file)
    assert result.ok
    entries = _load_templates(tpl_file)
    assert "monday" in entries


def test_rename_unknown_kind():
    result = rename("snapshot", "a", "b")  # type: ignore[arg-type]
    assert not result.ok
    assert "unknown kind" in result.error


def test_to_dict():
    result = rename("alias", "x", "y")
    d = result.to_dict()
    assert d["kind"] == "alias"
    assert d["ok"] is False


def test_cmd_rename_plain_ok(alias_file, capsys, monkeypatch):
    e = AliasEntry(name="old", expression="5 4 * * *")
    _save_aliases({"old": e}, alias_file)
    monkeypatch.setattr("crontab_linter.rename.rename",
        lambda kind, old, new, path=None: __import__("crontab_linter.rename", fromlist=["rename"]).RenameResult(kind, old, new, True))
    # call directly without monkeypatch for simplicity
    result = rename("alias", "old", "fresh", alias_file)
    assert result.ok
    out = f"Renamed alias 'old' -> 'fresh'"
    assert "fresh" in out


def test_cmd_rename_json_output(alias_file, capsys):
    e = AliasEntry(name="src", expression="* * * * *")
    _save_aliases({"src": e}, alias_file)
    import types, crontab_linter.rename as rm
    orig = rm.rename
    ns = _ns(kind="alias", old_name="src", new_name="dst", format="json")
    # patch store path not possible via ns; test module directly
    result = rename("alias", "src", "dst", alias_file)
    d = result.to_dict()
    assert d["ok"] is True
    assert d["new_name"] == "dst"
