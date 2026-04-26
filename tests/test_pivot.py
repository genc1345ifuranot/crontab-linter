"""Tests for crontab_linter.pivot and crontab_linter.pivot_formatter."""
from __future__ import annotations

import json

import pytest

from crontab_linter.pivot import pivot, _FIELD_NAMES
from crontab_linter.pivot_formatter import format_pivot, format_pivot_plain, format_pivot_json


# ---------------------------------------------------------------------------
# pivot() logic
# ---------------------------------------------------------------------------

def test_pivot_by_hour_groups_correctly():
    exprs = ["0 9 * * *", "30 9 * * *", "0 17 * * *"]
    result = pivot(exprs, "hour")
    assert result.pivot_field == "hour"
    assert "9" in result.groups
    assert "17" in result.groups
    assert set(result.groups["9"]) == {"0 9 * * *", "30 9 * * *"}
    assert result.groups["17"] == ["0 17 * * *"]


def test_pivot_by_minute():
    exprs = ["0 * * * *", "0 9 * * *", "15 * * * *"]
    result = pivot(exprs, "minute")
    assert "0" in result.groups
    assert "15" in result.groups
    assert len(result.groups["0"]) == 2


def test_pivot_groups_sorted_by_token():
    exprs = ["0 17 * * *", "0 3 * * *", "0 9 * * *"]
    result = pivot(exprs, "hour")
    keys = list(result.groups.keys())
    assert keys == sorted(keys)


def test_pivot_skips_blank_and_comment_lines():
    exprs = ["", "# this is a comment", "0 9 * * *"]
    result = pivot(exprs, "hour")
    assert "9" in result.groups
    assert not result.errors


def test_pivot_invalid_field_returns_error():
    result = pivot(["0 9 * * *"], "second")
    assert result.has_errors
    assert "second" in result.errors[0]
    assert result.groups == {}


def test_pivot_invalid_expression_recorded_in_errors():
    exprs = ["99 99 * * *", "0 9 * * *"]
    result = pivot(exprs, "hour")
    assert result.has_errors
    assert "9" in result.groups  # valid one still grouped


def test_pivot_all_invalid_returns_empty_groups():
    result = pivot(["99 99 * * *"], "hour")
    assert result.groups == {}
    assert result.has_errors


def test_pivot_wildcard_token_grouped():
    exprs = ["* * * * *", "* * * * 1"]
    result = pivot(exprs, "minute")
    assert "*" in result.groups
    assert len(result.groups["*"]) == 2


def test_pivot_to_dict_keys():
    result = pivot(["0 9 * * *"], "hour")
    d = result.to_dict()
    assert set(d.keys()) == {"pivot_field", "groups", "errors"}


# ---------------------------------------------------------------------------
# formatter
# ---------------------------------------------------------------------------

def test_format_plain_contains_field_name():
    result = pivot(["0 9 * * *"], "hour")
    out = format_pivot_plain(result)
    assert "hour" in out


def test_format_plain_shows_token_and_expression():
    result = pivot(["0 9 * * *"], "hour")
    out = format_pivot_plain(result)
    assert "[9]" in out
    assert "0 9 * * *" in out


def test_format_plain_shows_error():
    result = pivot(["99 99 * * *"], "hour")
    out = format_pivot_plain(result)
    assert "!" in out


def test_format_plain_no_valid_expressions_message():
    result = pivot([], "hour")
    out = format_pivot_plain(result)
    assert "no valid" in out


def test_format_json_is_valid_json():
    result = pivot(["0 9 * * *", "0 17 * * *"], "hour")
    out = format_pivot_json(result)
    data = json.loads(out)
    assert "groups" in data
    assert "pivot_field" in data


def test_format_dispatch_plain():
    result = pivot(["0 9 * * *"], "hour")
    assert format_pivot(result, "plain") == format_pivot_plain(result)


def test_format_dispatch_json():
    result = pivot(["0 9 * * *"], "hour")
    assert format_pivot(result, "json") == format_pivot_json(result)
