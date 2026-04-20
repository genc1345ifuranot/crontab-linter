"""Tests for crontab_linter.complexity."""
import pytest
from crontab_linter.complexity import compute_complexity, _level


def test_all_wildcards_is_simple():
    result = compute_complexity("* * * * *")
    assert result.score == 0
    assert result.level == "simple"
    assert result.reasons == []


def test_fixed_minute_adds_one_point():
    result = compute_complexity("30 * * * *")
    assert result.score == 1
    assert result.level == "simple"
    assert any("minute" in r for r in result.reasons)


def test_step_expression_adds_two_points():
    result = compute_complexity("*/15 * * * *")
    assert result.score == 2
    assert result.level == "simple"
    assert any("step" in r for r in result.reasons)


def test_range_adds_one_point():
    result = compute_complexity("* 9-17 * * *")
    assert result.score == 1
    assert any("range" in r for r in result.reasons)


def test_list_adds_count_points():
    # list with 3 values → +3
    result = compute_complexity("0 8,12,18 * * *")
    # hour list (3) + minute fixed (1) = 4
    assert result.score == 4
    assert result.level == "moderate"
    assert any("list" in r for r in result.reasons)


def test_complex_expression():
    # */5 (+2) in minute, 0,6,12,18 (+4) in hour, fixed dom (+1), fixed month (+1) = 8
    result = compute_complexity("*/5 0,6,12,18 1 6 *")
    assert result.score >= 8
    assert result.level == "complex"


def test_level_thresholds():
    assert _level(0) == "simple"
    assert _level(3) == "simple"
    assert _level(4) == "moderate"
    assert _level(7) == "moderate"
    assert _level(8) == "complex"
    assert _level(100) == "complex"


def test_to_dict_keys():
    result = compute_complexity("0 0 * * *")
    d = result.to_dict()
    assert set(d.keys()) == {"expression", "score", "level", "reasons"}
    assert d["expression"] == "0 0 * * *"


def test_expression_stored_on_result():
    expr = "5 4 * * 0"
    result = compute_complexity(expr)
    assert result.expression == expr


def test_multiple_fields_accumulate_reasons():
    # fixed minute + fixed hour + fixed dom
    result = compute_complexity("0 0 1 * *")
    assert len(result.reasons) == 3
