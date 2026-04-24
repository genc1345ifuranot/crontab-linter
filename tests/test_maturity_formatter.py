"""Tests for crontab_linter.maturity_formatter."""
import json
import pytest
from crontab_linter.maturity import MaturityResult
from crontab_linter.maturity_formatter import (
    format_maturity_plain,
    format_maturity_json,
    format_maturity,
)


def _result(score=85, grade="B", issues=None, tips=None):
    return MaturityResult(
        expression="0 9 * * 1-5",
        score=score,
        grade=grade,
        issues=issues or [],
        tips=tips or [],
    )


def test_plain_contains_score():
    out = format_maturity_plain(_result())
    assert "85/100" in out


def test_plain_contains_grade():
    out = format_maturity_plain(_result())
    assert "B" in out


def test_plain_no_issues_message():
    out = format_maturity_plain(_result())
    assert "No issues found" in out


def test_plain_shows_issues():
    out = format_maturity_plain(_result(issues=["Lint warning: runs every minute"]))
    assert "runs every minute" in out


def test_plain_shows_tips():
    out = format_maturity_plain(_result(tips=["Consider adding an alias."]))
    assert "Consider adding an alias" in out


def test_json_is_valid_json():
    out = format_maturity_json(_result())
    data = json.loads(out)
    assert data["score"] == 85
    assert data["grade"] == "B"


def test_json_contains_expression():
    out = format_maturity_json(_result())
    data = json.loads(out)
    assert data["expression"] == "0 9 * * 1-5"


def test_format_dispatch_plain():
    out = format_maturity(_result(), fmt="plain")
    assert "Score" in out


def test_format_dispatch_json():
    out = format_maturity(_result(), fmt="json")
    data = json.loads(out)
    assert "score" in data
