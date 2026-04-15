"""Tests for template CLI commands."""

import argparse
import json
import pytest

from crontab_linter.template_cli import cmd_save, cmd_get, cmd_delete, cmd_list


@pytest.fixture
def tpl_file(tmp_path):
    return str(tmp_path / "templates.json")


def _ns(**kwargs):
    defaults = {"template_file": None, "name": None, "expression": None,
                "description": "", "tags": ""}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_cmd_save_creates_template(tpl_file, capsys):
    args = _ns(template_file=tpl_file, name="daily", expression="0 0 * * *",
               description="Every midnight", tags="ops,daily")
    cmd_save(args)
    out = capsys.readouterr().out
    assert "daily" in out
    assert "saved" in out


def test_cmd_save_persists_to_file(tpl_file):
    args = _ns(template_file=tpl_file, name="weekly", expression="0 0 * * 0")
    cmd_save(args)
    with open(tpl_file) as f:
        data = json.load(f)
    assert any(d["name"] == "weekly" for d in data)


def test_cmd_get_existing(tpl_file, capsys):
    args_save = _ns(template_file=tpl_file, name="hourly", expression="0 * * * *",
                    description="Every hour", tags="")
    cmd_save(args_save)
    args_get = _ns(template_file=tpl_file, name="hourly")
    cmd_get(args_get)
    out = capsys.readouterr().out
    assert "hourly" in out
    assert "0 * * * *" in out


def test_cmd_get_missing_exits(tpl_file):
    args = _ns(template_file=tpl_file, name="nonexistent")
    with pytest.raises(SystemExit) as exc:
        cmd_get(args)
    assert exc.value.code == 1


def test_cmd_delete_existing(tpl_file, capsys):
    args_save = _ns(template_file=tpl_file, name="to_delete", expression="* * * * *")
    cmd_save(args_save)
    args_del = _ns(template_file=tpl_file, name="to_delete")
    cmd_delete(args_del)
    out = capsys.readouterr().out
    assert "deleted" in out


def test_cmd_delete_missing_exits(tpl_file):
    args = _ns(template_file=tpl_file, name="ghost")
    with pytest.raises(SystemExit) as exc:
        cmd_delete(args)
    assert exc.value.code == 1


def test_cmd_list_empty(tpl_file, capsys):
    args = _ns(template_file=tpl_file)
    cmd_list(args)
    out = capsys.readouterr().out
    assert "No templates" in out


def test_cmd_list_shows_entries(tpl_file, capsys):
    for name, expr in [("t1", "0 1 * * *"), ("t2", "0 2 * * *")]:
        cmd_save(_ns(template_file=tpl_file, name=name, expression=expr))
    capsys.readouterr()
    cmd_list(_ns(template_file=tpl_file))
    out = capsys.readouterr().out
    assert "t1" in out
    assert "t2" in out


def test_cmd_save_missing_name_exits(tpl_file):
    args = _ns(template_file=tpl_file, name="", expression="* * * * *")
    with pytest.raises(SystemExit) as exc:
        cmd_save(args)
    assert exc.value.code == 1


def test_cmd_save_tags_parsed(tpl_file):
    args = _ns(template_file=tpl_file, name="tagged", expression="0 0 * * *",
               tags="infra, ops, daily")
    cmd_save(args)
    with open(tpl_file) as f:
        data = json.load(f)
    entry = next(d for d in data if d["name"] == "tagged")
    assert "infra" in entry["tags"]
    assert "ops" in entry["tags"]
    assert "daily" in entry["tags"]
