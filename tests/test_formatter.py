"""Tests for crontab_linter.formatter module."""
import json
import pytest
from unittest.mock import MagicMock
from crontab_linter.formatter import (
    FormattedOutput,
    format_plain,
    format_json,
    build_output,
)
from crontab_linter.validator import ValidationResult
from crontab_linter.timezone import TimezoneCheckResult


def make_validation(valid=True, errors=None, warnings=None):
    vr = ValidationResult()
    vr.is_valid = valid
    vr.errors = errors or []
    vr.warnings = warnings or []
    return vr


def make_tz_result(valid=True, tz="UTC", dst=False, dst_msg=None, msg=None):
    tr = MagicMock(spec=TimezoneCheckResult)
    tr.is_valid = valid
    tr.timezone = tz
    tr.dst_ambiguous = dst
    tr.dst_message = dst_msg or ""
    tr.message = msg or ""
    return tr


def test_format_plain_valid():
    output = FormattedOutput(
        expression="0 * * * *",
        is_valid=True,
        explanation="Every hour",
        warnings=[],
        errors=[],
        timezone_info="UTC",
    )
    text = format_plain(output)
    assert "VALID" in text
    assert "0 * * * *" in text
    assert "Every hour" in text
    assert "UTC" in text


def test_format_plain_invalid():
    output = FormattedOutput(
        expression="99 * * * *",
        is_valid=False,
        explanation=None,
        warnings=[],
        errors=["Minute out of range"],
        timezone_info=None,
    )
    text = format_plain(output)
    assert "INVALID" in text
    assert "[ERROR]" in text
    assert "Minute out of range" in text


def test_format_plain_with_warning():
    output = FormattedOutput(
        expression="0 2 * * *",
        is_valid=True,
        explanation="At 2am",
        warnings=["DST ambiguity detected"],
        errors=[],
        timezone_info="America/New_York",
    )
    text = format_plain(output)
    assert "[WARN]" in text
    assert "DST ambiguity detected" in text


def test_format_json_structure():
    output = FormattedOutput(
        expression="*/5 * * * *",
        is_valid=True,
        explanation="Every 5 minutes",
        warnings=[],
        errors=[],
        timezone_info="Europe/London",
    )
    text = format_json(output)
    data = json.loads(text)
    assert data["expression"] == "*/5 * * * *"
    assert data["valid"] is True
    assert data["explanation"] == "Every 5 minutes"
    assert data["timezone"] == "Europe/London"
    assert data["errors"] == []
    assert data["warnings"] == []


def test_build_output_no_timezone():
    vr = make_validation(valid=True, warnings=["some warning"])
    out = build_output("* * * * *", vr, "Every minute")
    assert out.is_valid is True
    assert out.explanation == "Every minute"
    assert "some warning" in out.warnings
    assert out.timezone_info is None


def test_build_output_with_valid_timezone():
    vr = make_validation()
    tr = make_tz_result(valid=True, tz="Asia/Tokyo")
    out = build_output("0 9 * * *", vr, "At 9am", tz_result=tr)
    assert out.timezone_info == "Asia/Tokyo"
    assert out.warnings == []


def test_build_output_with_invalid_timezone():
    vr = make_validation()
    tr = make_tz_result(valid=False, msg="Unknown timezone")
    out = build_output("0 9 * * *", vr, "At 9am", tz_result=tr)
    assert out.timezone_info is None
    assert any("Unknown timezone" in w for w in out.warnings)


def test_build_output_with_dst_ambiguity():
    vr = make_validation()
    tr = make_tz_result(valid=True, tz="America/Chicago", dst=True, dst_msg="Clock change at 2am")
    out = build_output("0 2 * * *", vr, "At 2am", tz_result=tr)
    assert any("Clock change at 2am" in w for w in out.warnings)
