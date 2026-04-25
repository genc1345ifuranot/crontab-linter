"""Tests for crontab_linter.truncate."""
import pytest
from crontab_linter.truncate import truncate, FIELD_NAMES


def test_truncate_minute_only():
    result = truncate("30 6 * * 1", ["minute"])
    assert result.ok
    assert result.truncated == "* 6 * * 1"
    assert result.fields_cleared == ["minute"]


def test_truncate_hour_only():
    result = truncate("0 12 * * *", ["hour"])
    assert result.ok
    assert result.truncated == "0 * * * *"
    assert result.fields_cleared == ["hour"]


def test_truncate_multiple_fields():
    result = truncate("15 8 1 6 *", ["minute", "hour", "month"])
    assert result.ok
    assert result.truncated == "* * 1 * *"
    assert set(result.fields_cleared) == {"minute", "hour", "month"}


def test_truncate_already_wildcard_not_reported():
    result = truncate("0 * * * *", ["hour"])
    assert result.ok
    assert result.truncated == "0 * * * *"
    assert result.fields_cleared == []  # already wild, nothing changed


def test_truncate_all_fields():
    result = truncate("5 4 3 2 1", FIELD_NAMES)
    assert result.ok
    assert result.truncated == "* * * * *"
    assert len(result.fields_cleared) == 5


def test_truncate_unknown_field_returns_error():
    result = truncate("* * * * *", ["second"])
    assert not result.ok
    assert result.truncated is None
    assert any("second" in e for e in result.errors)


def test_truncate_mixed_unknown_and_known_returns_error():
    result = truncate("* * * * *", ["minute", "bogus"])
    assert not result.ok
    assert "bogus" in result.errors[0]


def test_truncate_invalid_expression_returns_error():
    result = truncate("99 99 99 99 99", ["minute"])
    assert not result.ok
    assert result.truncated is None
    assert result.errors


def test_truncate_to_dict_keys():
    result = truncate("0 9 * * 1", ["hour"])
    d = result.to_dict()
    assert set(d.keys()) == {"original", "truncated", "fields_cleared", "ok", "errors"}


def test_truncate_to_dict_values():
    result = truncate("0 9 * * 1", ["hour"])
    d = result.to_dict()
    assert d["original"] == "0 9 * * 1"
    assert d["truncated"] == "0 * * * 1"
    assert d["ok"] is True
    assert d["fields_cleared"] == ["hour"]


def test_truncate_preserves_day_of_week():
    result = truncate("0 0 * * 5", ["minute", "hour"])
    assert result.ok
    assert result.truncated == "* * * * 5"


def test_truncate_no_fields_is_noop():
    result = truncate("30 6 15 3 1", [])
    assert result.ok
    assert result.truncated == "30 6 15 3 1"
    assert result.fields_cleared == []
