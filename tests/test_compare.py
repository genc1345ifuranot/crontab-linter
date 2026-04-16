"""Tests for compare module and compare_formatter."""
import json
import pytest
from crontab_linter.compare import compare
from crontab_linter.compare_formatter import format_compare


def test_compare_identical_expressions():
    result = compare("0 9 * * 1", "0 9 * * 1")
    assert result.valid_a
    assert result.valid_b
    assert not result.has_diff()


def test_compare_different_minute():
    result = compare("0 9 * * 1", "30 9 * * 1")
    assert result.has_diff()
    changed = [fd.field_name for fd in result.diff.changed_fields()]
    assert "minute" in changed


def test_compare_both_valid_sets_explanations():
    result = compare("0 0 * * *", "0 12 * * *")
    assert result.explanation_a != ""
    assert result.explanation_b != ""


def test_compare_invalid_a_returns_errors():
    result = compare("99 * * * *", "0 * * * *")
    assert not result.valid_a
    assert result.errors_a


def test_compare_invalid_b_returns_errors():
    result = compare("0 * * * *", "0 99 * * *")
    assert not result.valid_b
    assert result.errors_b


def test_compare_no_diff_when_invalid():
    result = compare("99 * * * *", "0 99 * * *")
    assert result.diff is None


def test_format_compare_plain_no_diff():
    result = compare("0 9 * * 1", "0 9 * * 1")
    output = format_compare(result, fmt="plain")
    assert "No differences found" in output
    assert "A:" in output
    assert "B:" in output


def test_format_compare_plain_with_diff():
    result = compare("0 9 * * 1", "30 9 * * 1")
    output = format_compare(result, fmt="plain")
    assert "Changes:" in output
    assert "minute" in output


def test_format_compare_json_structure():
    result = compare("0 9 * * *", "0 10 * * *")
    output = format_compare(result, fmt="json")
    data = json.loads(output)
    assert "a" in data and "b" in data and "diff" in data
    assert isinstance(data["diff"], list)
    assert data["diff"][0]["field"] == "hour"


def test_format_compare_json_invalid():
    result = compare("99 * * * *", "0 * * * *")
    output = format_compare(result, fmt="json")
    data = json.loads(output)
    assert not data["a"]["valid")
    assert data["diff"] is None
