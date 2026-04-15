"""Tests for crontab_linter.lint_rules."""
import pytest
from crontab_linter.parser import CronExpression
from crontab_linter.lint_rules import lint, LintResult, LintWarning


def _parse(expr: str) -> CronExpression:
    return CronExpression.parse(expr)


def test_every_minute_triggers_warning():
    result = lint(_parse("* * * * *"))
    codes = [w.code for w in result.warnings]
    assert "EVERY_MINUTE" in codes


def test_every_minute_severity_is_warning():
    result = lint(_parse("* * * * *"))
    w = next(w for w in result.warnings if w.code == "EVERY_MINUTE")
    assert w.severity == "warning"


def test_no_every_minute_when_hour_fixed():
    result = lint(_parse("* 3 * * *"))
    codes = [w.code for w in result.warnings]
    assert "EVERY_MINUTE" not in codes


def test_midnight_only_info():
    result = lint(_parse("0 0 * * *"))
    codes = [w.code for w in result.warnings]
    assert "MIDNIGHT_ONLY" in codes
    w = next(w for w in result.warnings if w.code == "MIDNIGHT_ONLY")
    assert w.severity == "info"


def test_no_midnight_warning_for_other_times():
    result = lint(_parse("0 6 * * *"))
    codes = [w.code for w in result.warnings]
    assert "MIDNIGHT_ONLY" not in codes


def test_high_frequency_minute_step_1():
    result = lint(_parse("*/1 * * * *"))
    codes = [w.code for w in result.warnings]
    assert "HIGH_FREQUENCY_MINUTE" in codes


def test_high_frequency_minute_step_2():
    result = lint(_parse("*/2 * * * *"))
    codes = [w.code for w in result.warnings]
    assert "HIGH_FREQUENCY_MINUTE" in codes


def test_no_high_frequency_minute_step_5():
    result = lint(_parse("*/5 * * * *"))
    codes = [w.code for w in result.warnings]
    assert "HIGH_FREQUENCY_MINUTE" not in codes


def test_high_frequency_hour_step_1_info():
    result = lint(_parse("0 */1 * * *"))
    codes = [w.code for w in result.warnings]
    assert "HIGH_FREQUENCY_HOUR" in codes
    w = next(w for w in result.warnings if w.code == "HIGH_FREQUENCY_HOUR")
    assert w.severity == "info"


def test_friday_13th_pattern():
    result = lint(_parse("0 0 13 * 5"))
    codes = [w.code for w in result.warnings]
    assert "FRIDAY_13TH" in codes
    w = next(w for w in result.warnings if w.code == "FRIDAY_13TH")
    assert w.severity == "info"


def test_no_friday_13th_on_monday():
    result = lint(_parse("0 0 13 * 1"))
    codes = [w.code for w in result.warnings]
    assert "FRIDAY_13TH" not in codes


def test_lint_result_has_warnings_false_when_clean():
    result = lint(_parse("30 9 * * 1-5"))
    assert not result.has_warnings


def test_lint_result_to_dict():
    result = lint(_parse("* * * * *"))
    d = result.to_dict()
    assert "warnings" in d
    assert isinstance(d["warnings"], list)
    assert all("code" in w and "message" in w and "severity" in w for w in d["warnings"])


def test_lint_warning_to_dict():
    w = LintWarning(code="TEST", message="test message", severity="info")
    assert w.to_dict() == {"code": "TEST", "message": "test message", "severity": "info"}
