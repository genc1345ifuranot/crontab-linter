"""Tests for suggest module."""
import json
import pytest
from crontab_linter.suggest import suggest, Suggestion
from crontab_linter.suggest_formatter import format_suggest


def test_valid_expression_no_suggestions():
    r = suggest("0 9 * * 1")
    assert not r.has_suggestions
    assert r.suggestions == []


def test_minute_out_of_range():
    r = suggest("60 9 * * *")
    assert r.has_suggestions
    reasons = [s.reason for s in r.suggestions]
    assert any("minute" in reason for reason in reasons)


def test_hour_out_of_range():
    r = suggest("0 25 * * *")
    assert r.has_suggestions
    fixed = r.suggestions[0].fixed
    assert int(fixed) <= 23


def test_dom_out_of_range():
    r = suggest("0 0 32 * *")
    assert r.has_suggestions
    assert r.suggestions[0].fixed == "31"


def test_month_out_of_range():
    r = suggest("0 0 1 13 *")
    assert r.has_suggestions
    assert r.suggestions[0].fixed == "12"


def test_dow_out_of_range():
    r = suggest("0 0 * * 8")
    assert r.has_suggestions
    assert r.suggestions[0].fixed == "7"


def test_step_out_of_range():
    r = suggest("*/0 * * * *")
    assert r.has_suggestions
    assert r.suggestions[0].fixed == "*/1"


def test_too_few_fields_padded():
    r = suggest("0 9")
    assert r.has_suggestions
    assert "Padded" in r.suggestions[0].reason
    fixed_parts = r.suggestions[0].fixed.split()
    assert len(fixed_parts) == 5


def test_format_plain_no_suggestions():
    r = suggest("*/5 * * * *")
    out = format_suggest(r, fmt="plain")
    assert "No suggestions" in out


def test_format_plain_with_suggestions():
    r = suggest("60 9 * * *")
    out = format_suggest(r, fmt="plain")
    assert "->" in out
    assert "Suggested fix" in out


def test_format_json_structure():
    r = suggest("0 25 * * *")
    out = format_suggest(r, fmt="json")
    data = json.loads(out)
    assert "expression" in data
    assert "suggestions" in data
    assert data["has_suggestions"] is True
    assert data["suggestions"][0]["original"] == "25"
