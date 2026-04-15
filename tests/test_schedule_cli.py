"""Tests for crontab_linter.schedule_cli."""

from __future__ import annotations

import argparse
import sys

import pytest

from crontab_linter.schedule_cli import build_schedule_parser, cmd_schedule


def _ns(**kwargs) -> argparse.Namespace:
    defaults = {
        "expression": "0 12 * * *",
        "timezone": "UTC",
        "count": 3,
        "format": "plain",
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_cmd_schedule_plain(capsys):
    rc = cmd_schedule(_ns())
    out = capsys.readouterr().out
    assert rc == 0
    assert "0 12 * * *" in out
    assert "UTC" in out


def test_cmd_schedule_json(capsys):
    import json
    rc = cmd_schedule(_ns(format="json"))
    out = capsys.readouterr().out
    assert rc == 0
    data = json.loads(out)
    assert data["expression"] == "0 12 * * *"
    assert len(data["next_runs"]) == 3


def test_cmd_schedule_count(capsys):
    import json
    rc = cmd_schedule(_ns(count=7, format="json"))
    out = capsys.readouterr().out
    assert rc == 0
    data = json.loads(out)
    assert len(data["next_runs"]) == 7


def test_cmd_schedule_bad_timezone(capsys):
    rc = cmd_schedule(_ns(timezone="Fake/Zone"))
    out = capsys.readouterr().out
    assert rc == 1
    assert "Error" in out


def test_cmd_schedule_preset(capsys):
    rc = cmd_schedule(_ns(expression="@daily"))
    out = capsys.readouterr().out
    assert rc == 0
    # @daily resolves to '0 0 * * *'
    assert "0 0 * * *" in out


def test_cmd_schedule_bad_expression(capsys):
    rc = cmd_schedule(_ns(expression="not a cron"))
    err = capsys.readouterr().err
    assert rc == 1
    assert "Parse error" in err


def test_build_schedule_parser():
    root = argparse.ArgumentParser()
    sub = root.add_subparsers()
    build_schedule_parser(sub)
    args = root.parse_args(["schedule", "*/5 * * * *", "--count", "2", "--timezone", "Europe/London"])
    assert args.expression == "*/5 * * * *"
    assert args.count == 2
    assert args.timezone == "Europe/London"
    assert args.format == "plain"
