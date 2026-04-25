"""Tests for crontab_linter.interpolate_cli."""
from __future__ import annotations

import argparse
import sys

import pytest

from crontab_linter.interpolate_cli import cmd_interpolate, build_interpolate_parser


def _ns(**kwargs) -> argparse.Namespace:
    defaults = {"expression": "* * * * *", "var": None, "format": "plain"}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_cmd_interpolate_plain_output(capsys):
    cmd_interpolate(_ns(expression="${MIN} * * * *", var=["MIN=5"]))
    out = capsys.readouterr().out
    assert "5 * * * *" in out
    assert "MIN" in out


def test_cmd_interpolate_json_output(capsys):
    cmd_interpolate(_ns(expression="*/5 * * * *", format="json"))
    out = capsys.readouterr().out
    assert "\"interpolated\"" in out
    assert "*/5 * * * *" in out


def test_cmd_interpolate_missing_var_exits(capsys):
    with pytest.raises(SystemExit) as exc:
        cmd_interpolate(_ns(expression="${MISSING} * * * *"))
    assert exc.value.code == 1


def test_cmd_interpolate_bad_var_format_exits(capsys):
    with pytest.raises(SystemExit) as exc:
        cmd_interpolate(_ns(expression="* * * * *", var=["NOEQUALS"]))
    assert exc.value.code == 2


def test_build_interpolate_parser():
    root = argparse.ArgumentParser()
    subs = root.add_subparsers()
    p = build_interpolate_parser(subs)
    assert p is not None


def test_multiple_vars_substituted(capsys):
    cmd_interpolate(_ns(expression="${A} ${B} * * *", var=["A=0", "B=12"]))
    out = capsys.readouterr().out
    assert "0 12 * * *" in out
