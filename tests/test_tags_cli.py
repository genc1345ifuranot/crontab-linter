"""Tests for crontab_linter/tags_cli.py"""

from __future__ import annotations

import argparse
import json

import pytest

from crontab_linter.tags import tag_expression
from crontab_linter.tags_cli import cmd_list, cmd_remove_tag, cmd_tag


@pytest.fixture()
def tag_file(tmp_path):
    return str(tmp_path / "tags.json")


def _ns(**kwargs) -> argparse.Namespace:
    defaults = {"tags_file": None, "note": "", "json": False, "filter_tag": None}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_cmd_tag_creates_entry(tag_file, capsys):
    cmd_tag(_ns(expression="0 * * * *", tags="hourly,prod", tags_file=tag_file))
    captured = capsys.readouterr()
    assert "hourly" in captured.out
    assert "prod" in captured.out


def test_cmd_tag_empty_tags_exits(tag_file):
    with pytest.raises(SystemExit):
        cmd_tag(_ns(expression="0 * * * *", tags="  , ", tags_file=tag_file))


def test_cmd_list_empty(tag_file, capsys):
    cmd_list(_ns(tags_file=tag_file, filter_tag=None))
    captured = capsys.readouterr()
    assert "No tagged" in captured.out


def test_cmd_list_shows_entries(tag_file, capsys):
    tag_expression("0 * * * *", ["hourly"], path=tag_file)
    cmd_list(_ns(tags_file=tag_file, filter_tag=None))
    captured = capsys.readouterr()
    assert "0 * * * *" in captured.out
    assert "hourly" in captured.out


def test_cmd_list_filter_by_tag(tag_file, capsys):
    tag_expression("0 * * * *", ["hourly"], path=tag_file)
    tag_expression("0 0 * * *", ["daily"], path=tag_file)
    cmd_list(_ns(tags_file=tag_file, filter_tag="daily"))
    captured = capsys.readouterr()
    assert "0 0 * * *" in captured.out
    assert "0 * * * *" not in captured.out


def test_cmd_list_filter_no_match(tag_file, capsys):
    tag_expression("0 * * * *", ["hourly"], path=tag_file)
    cmd_list(_ns(tags_file=tag_file, filter_tag="nonexistent"))
    captured = capsys.readouterr()
    assert "No expressions tagged" in captured.out


def test_cmd_list_json_output(tag_file, capsys):
    tag_expression("0 * * * *", ["hourly"], path=tag_file)
    cmd_list(_ns(tags_file=tag_file, filter_tag=None, **{"json": True}))
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert isinstance(data, list)
    assert data[0]["expression"] == "0 * * * *"


def test_cmd_remove_tag_success(tag_file, capsys):
    tag_expression("0 * * * *", ["hourly", "prod"], path=tag_file)
    cmd_remove_tag(_ns(expression="0 * * * *", tag="prod", tags_file=tag_file))
    captured = capsys.readouterr()
    assert "prod" in captured.out
    assert "hourly" in captured.out


def test_cmd_remove_tag_missing_expression_exits(tag_file):
    with pytest.raises(SystemExit):
        cmd_remove_tag(_ns(expression="9 9 9 9 9", tag="prod", tags_file=tag_file))
