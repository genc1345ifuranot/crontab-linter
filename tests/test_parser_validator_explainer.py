"""Tests for parser, validator, and explainer modules."""

import pytest

from crontab_linter.parser import parse
from crontab_linter.validator import validate
from crontab_linter.explainer import explain


# --- Parser tests ---

def test_parse_wildcard_expression():
    expr = parse("* * * * *")
    assert expr is not None
    assert len(expr.fields) == 5
    assert expr.minute.values == list(range(0, 60))


def test_parse_step_expression():
    expr = parse("*/15 * * * *")
    assert expr.minute.values == [0, 15, 30, 45]


def test_parse_range_expression():
    expr = parse("0 9-17 * * *")
    assert expr.hour.values == list(range(9, 18))


def test_parse_list_expression():
    expr = parse("0 8,12,18 * * *")
    assert expr.hour.values == [8, 12, 18]


def test_parse_month_alias():
    expr = parse("0 0 1 jan *")
    assert expr.month.values == [1]


def test_parse_dow_alias():
    expr = parse("0 0 * * mon")
    assert expr.day_of_week.values == [1]


def test_parse_invalid_field_count():
    assert parse("* * * *") is None


# --- Validator tests ---

def test_validate_valid_expression():
    result = validate("0 12 * * *")
    assert result.is_valid
    assert not result.errors


def test_validate_wrong_field_count():
    result = validate("0 12 *")
    assert not result.is_valid
    assert any("5 fields" in e for e in result.errors)


def test_validate_minute_out_of_range():
    result = validate("60 * * * *")
    assert not result.is_valid
    assert any("minute" in e for e in result.errors)


def test_validate_hour_out_of_range():
    result = validate("0 24 * * *")
    assert not result.is_valid


def test_validate_dom_dow_conflict_warning():
    result = validate("0 12 15 * 1")
    assert result.is_valid
    assert any("OR logic" in w for w in result.warnings)


def test_validate_unreachable_day31():
    result = validate("0 0 31 4 *")
    assert result.is_valid
    assert any("31" in w for w in result.warnings)


# --- Explainer tests ---

def test_explain_every_minute():
    expr = parse("* * * * *")
    text = explain(expr)
    assert "every minute" in text


def test_explain_specific_hour():
    expr = parse("0 9 * * *")
    text = explain(expr)
    assert "09:00" in text


def test_explain_with_month():
    expr = parse("0 0 1 1 *")
    text = explain(expr)
    assert "January" in text


def test_explain_with_dow():
    expr = parse("0 8 * * 1")
    text = explain(expr)
    assert "Monday" in text


def test_explain_step():
    expr = parse("*/30 * * * *")
    text = explain(expr)
    assert "30" in text
