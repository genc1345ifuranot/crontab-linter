"""Tests for crontab_linter.frequency."""
import pytest
from crontab_linter.frequency import compute_frequency, _count_values


# ---------------------------------------------------------------------------
# _count_values unit tests
# ---------------------------------------------------------------------------

def test_count_wildcard_minute():
    assert _count_values("*", 0, 59) == 60


def test_count_wildcard_hour():
    assert _count_values("*", 0, 23) == 24


def test_count_specific_value():
    assert _count_values("5", 0, 59) == 1


def test_count_range():
    assert _count_values("1-5", 0, 59) == 5


def test_count_step():
    assert _count_values("*/15", 0, 59) == 4


def test_count_list():
    assert _count_values("0,15,30,45", 0, 59) == 4


def test_count_step_with_range():
    assert _count_values("0-30/10", 0, 59) == 4  # 0,10,20,30


# ---------------------------------------------------------------------------
# compute_frequency integration tests
# ---------------------------------------------------------------------------

def test_every_minute_fires_1440_per_day():
    result = compute_frequency("* * * * *")
    assert result.valid
    assert result.fires_per_day == 1440.0


def test_every_minute_description():
    result = compute_frequency("* * * * *")
    assert result.description == "every minute"


def test_hourly_fires_24_per_day():
    result = compute_frequency("0 * * * *")
    assert result.valid
    assert result.fires_per_day == 24.0


def test_daily_midnight_fires_once():
    result = compute_frequency("0 0 * * *")
    assert result.valid
    assert result.fires_per_day == 1.0


def test_every_15_minutes_fires_96_per_day():
    result = compute_frequency("*/15 * * * *")
    assert result.valid
    assert result.fires_per_day == 96.0


def test_fires_per_hour_for_every_minute():
    result = compute_frequency("* * * * *")
    assert result.fires_per_hour == 60.0


def test_fires_per_minute_for_every_minute():
    result = compute_frequency("* * * * *")
    assert abs(result.fires_per_minute - 1.0) < 0.001


def test_invalid_expression_returns_errors():
    result = compute_frequency("99 * * * *")
    assert not result.valid
    assert result.fires_per_day == 0.0
    assert len(result.errors) > 0


def test_invalid_expression_description():
    result = compute_frequency("99 * * * *")
    assert result.description == "invalid expression"


def test_to_dict_keys():
    result = compute_frequency("0 0 * * *")
    d = result.to_dict()
    assert set(d.keys()) == {
        "expression", "fires_per_day", "fires_per_hour",
        "fires_per_minute", "description", "valid", "errors",
    }


def test_monthly_expression_less_than_once_a_day():
    result = compute_frequency("0 9 1 * *")
    assert result.valid
    assert result.fires_per_day < 1.0
    assert result.description == "less than once a day"


def test_expression_stored_on_result():
    expr = "30 6 * * 1"
    result = compute_frequency(expr)
    assert result.expression == expr
