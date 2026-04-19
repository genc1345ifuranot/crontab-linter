import argparse
import pytest
from pathlib import Path
from unittest.mock import patch
from crontab_linter.remind import add_reminder
from crontab_linter.remind_cli import cmd_add, cmd_get, cmd_remove, cmd_list


@pytest.fixture
def rfile(tmp_path):
    return tmp_path / "reminders.json"


def _ns(**kwargs):
    defaults = {"format": "plain", "tags": ""}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_cmd_add_creates_entry(rfile, capsys):
    with patch("crontab_linter.remind_cli.add_reminder", wraps=lambda *a, **kw: add_reminder(*a, **kw)) as m:
        m.side_effect = None
    add_reminder("0 9 * * 1", "Standup", path=rfile)
    entry = _ns(expression="0 9 * * 1", message="Standup")
    with patch("crontab_linter.remind_cli.add_reminder", return_value=add_reminder("0 9 * * 1", "Standup", path=rfile)):
        cmd_add(entry)
    out = capsys.readouterr().out
    assert "Standup" in out


def test_cmd_get_existing(rfile, capsys):
    add_reminder("*/10 * * * *", "Check metrics", path=rfile)
    ns = _ns(expression="*/10 * * * *")
    with patch("crontab_linter.remind_cli.get_reminder", return_value=add_reminder("*/10 * * * *", "Check metrics", path=rfile)):
        cmd_get(ns)
    out = capsys.readouterr().out
    assert "Check metrics" in out


def test_cmd_get_missing_exits(rfile):
    ns = _ns(expression="1 2 3 4 5")
    with patch("crontab_linter.remind_cli.get_reminder", return_value=None):
        with pytest.raises(SystemExit):
            cmd_get(ns)


def test_cmd_remove_existing(rfile, capsys):
    ns = _ns(expression="0 0 * * *")
    with patch("crontab_linter.remind_cli.remove_reminder", return_value=True):
        cmd_remove(ns)
    assert "removed" in capsys.readouterr().out


def test_cmd_remove_missing_exits(rfile):
    ns = _ns(expression="0 0 * * *")
    with patch("crontab_linter.remind_cli.remove_reminder", return_value=False):
        with pytest.raises(SystemExit):
            cmd_remove(ns)


def test_cmd_list_empty(rfile, capsys):
    ns = _ns()
    with patch("crontab_linter.remind_cli.list_reminders", return_value=[]):
        cmd_list(ns)
    assert "No reminders" in capsys.readouterr().out


def test_cmd_list_json(rfile, capsys):
    add_reminder("0 6 * * *", "Morning", path=rfile)
    ns = _ns(format="json")
    with patch("crontab_linter.remind_cli.list_reminders", return_value=[add_reminder("0 6 * * *", "Morning", path=rfile)]):
        cmd_list(ns)
    import json
    data = json.loads(capsys.readouterr().out)
    assert isinstance(data, list)
    assert data[0]["message"] == "Morning"
