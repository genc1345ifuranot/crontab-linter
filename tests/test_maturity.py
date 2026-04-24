"""Tests for crontab_linter.maturity."""
import pytest
from crontab_linter.maturity import assess_maturity, _grade


def test_grade_boundaries():
    assert _grade(100) == "A"
    assert _grade(90) == "A"
    assert _grade(89) == "B"
    assert _grade(75) == "B"
    assert _grade(74) == "C"
    assert _grade(60) == "C"
    assert _grade(59) == "D"
    assert _grade(40) == "D"
    assert _grade(39) == "F"
    assert _grade(0) == "F"


def test_valid_simple_expression_high_score():
    result = assess_maturity("0 9 * * 1-5")
    assert result.score >= 75
    assert result.grade in ("A", "B")
    assert result.expression == "0 9 * * 1-5"


def test_invalid_expression_penalised():
    result = assess_maturity("99 25 * * *")
    assert result.score < 60
    assert len(result.issues) > 0


def test_every_minute_gets_tip():
    result = assess_maturity("* * * * *")
    combined = result.issues + result.tips
    assert any("every minute" in t.lower() or "intentional" in t.lower() for t in combined)


def test_to_dict_keys():
    result = assess_maturity("0 0 * * *")
    d = result.to_dict()
    assert set(d.keys()) == {"expression", "score", "grade", "issues", "tips"}


def test_score_clamped_to_zero_for_very_bad_expr():
    # Pile up many invalid fields
    result = assess_maturity("99 99 99 99 99")
    assert result.score >= 0


def test_score_never_exceeds_100():
    result = assess_maturity("0 12 * * *")
    assert result.score <= 100


def test_preset_expression_scores_well():
    result = assess_maturity("0 0 1 * *")
    assert result.grade in ("A", "B", "C")


def test_issues_list_populated_for_invalid():
    result = assess_maturity("60 * * * *")
    assert isinstance(result.issues, list)
    assert len(result.issues) >= 1


def test_tips_list_is_list():
    result = assess_maturity("0 6 * * *")
    assert isinstance(result.tips, list)
