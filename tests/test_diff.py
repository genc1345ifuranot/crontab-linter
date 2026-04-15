"""Tests for crontab expression diff feature."""

import json
import pytest

from crontab_linter.diff import diff_expressions, CronDiff, FieldDiff
from crontab_linter.diff_formatter import format_diff_plain, format_diff_json, format_diff


def test_diff_no_changes():
    result = diff_expressions("0 9 * * 1", "0 9 * * 1")
    assert isinstance(result, CronDiff)
    assert not result.has_changes
    assert result.changed_fields == []


def test_diff_single_field_change():
    result = diff_expressions("0 9 * * 1", "0 10 * * 1")
    assert result.has_changes
    changed = result.changed_fields
    assert len(changed) == 1
    assert changed[0].name == "hour"
    assert changed[0].old_value == "9"
    assert changed[0].new_value == "10"


def test_diff_multiple_fields_changed():
    result = diff_expressions("0 9 * * 1", "30 18 1 * *")
    assert result.has_changes
    names = {f.name for f in result.changed_fields}
    assert "minute" in names
    assert "hour" in names
    assert "day_of_month" in names
    assert "day_of_week" in names


def test_diff_wildcard_unchanged():
    result = diff_expressions("* * * * *", "* * * * *")
    assert not result.has_changes
    for f in result.fields:
        assert not f.changed


def test_diff_stores_explanations():
    result = diff_expressions("0 9 * * 1", "0 10 * * 1")
    assert result.old_explanation != ""
    assert result.new_explanation != ""
    assert result.old_explanation != result.new_explanation


def test_format_plain_no_changes():
    result = diff_expressions("0 9 * * *", "0 9 * * *")
    output = format_diff_plain(result)
    assert "No differences found" in output
    assert "0 9 * * *" in output


def test_format_plain_with_changes():
    result = diff_expressions("0 9 * * *", "0 17 * * *")
    output = format_diff_plain(result)
    assert "hour" in output
    assert "->" in output
    assert "Old schedule" in output
    assert "New schedule" in output


def test_format_json_structure():
    result = diff_expressions("0 9 * * 1", "0 10 * * 1")
    output = format_diff_json(result)
    data = json.loads(output)
    assert data["old_expr"] == "0 9 * * 1"
    assert data["new_expr"] == "0 10 * * 1"
    assert data["has_changes"] is True
    assert len(data["fields"]) == 5
    assert "old_explanation" in data
    assert "new_explanation" in data


def test_format_json_no_changes():
    result = diff_expressions("*/5 * * * *", "*/5 * * * *")
    output = format_diff_json(result)
    data = json.loads(output)
    assert data["has_changes"] is False
    assert all(not f["changed"] for f in data["fields"])


def test_format_dispatch_plain():
    result = diff_expressions("0 0 * * *", "0 1 * * *")
    assert format_diff(result, "plain") == format_diff_plain(result)


def test_format_dispatch_json():
    result = diff_expressions("0 0 * * *", "0 1 * * *")
    assert format_diff(result, "json") == format_diff_json(result)
