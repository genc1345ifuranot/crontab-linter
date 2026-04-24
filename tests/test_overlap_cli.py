"""Tests for crontab_linter.overlap_cli."""
from __future__ import annotations

import argparse
import sys
import pytest

from crontab_linter.overlap_cli import cmd_overlap, build_overlap_parser


def _ns(**kwargs) -> argparse.Namespace:
    defaults = {
        "expressions": ["0 6 * * *", "0 18 * * *"],
        "start": None,
        "minutes": 1440,
        "format": "plain",
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_cmd_overlap_plain_no_overlap(capsys):
    cmd_overlap(_ns())
    out = capsys.readouterr().out
    assert "No scheduling overlaps" in out


def test_cmd_overlap_plain_with_overlap(capsys):
    cmd_overlap(_ns(expressions=["0 6 * * *", "0 6 * * *"]))
    out = capsys.readouterr().out
    assert "overlapping pair" in out


def test_cmd_overlap_json_output(capsys):
    cmd_overlap(_ns(format="json"))
    out = capsys.readouterr().out
    assert "has_overlaps" in out


def test_cmd_overlap_too_few_expressions_exits():
    with pytest.raises(SystemExit) as exc:
        cmd_overlap(_ns(expressions=["0 6 * * *"]))
    assert exc.value.code == 1


def test_cmd_overlap_bad_start_exits():
    with pytest.raises(SystemExit) as exc:
        cmd_overlap(_ns(start="not-a-date"))
    assert exc.value.code == 1


def test_cmd_overlap_valid_start_iso(capsys):
    cmd_overlap(_ns(start="2024-06-01T00:00:00"))
    out = capsys.readouterr().out
    assert out  # just ensure it ran


def test_build_overlap_parser_registers_subcommand():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()
    build_overlap_parser(sub)
    args = parser.parse_args(["overlap", "0 6 * * *", "0 18 * * *"])
    assert args.expressions == ["0 6 * * *", "0 18 * * *"]
    assert args.minutes == 1440
    assert args.format == "plain"
