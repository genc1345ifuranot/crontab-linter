"""Tests for crontab_linter.coverage and coverage_formatter."""
from __future__ import annotations

import json

import pytest

from crontab_linter.coverage import compute_coverage, CoverageResult
from crontab_linter.coverage_formatter import (
    format_coverage_plain,
    format_coverage_json,
    format_coverage,
)


# ---------------------------------------------------------------------------
# compute_coverage
# ---------------------------------------------------------------------------

def test_wildcard_expression_full_coverage():
    result = compute_coverage("* * * * *")
    assert result.ok
    assert result.fields["minute"].ratio == pytest.approx(1.0)
    assert result.fields["hour"].ratio == pytest.approx(1.0)
    assert result.fields["day_of_month"].ratio == pytest.approx(1.0)
    assert result.fields["month"].ratio == pytest.approx(1.0)
    assert result.fields["day_of_week"].ratio == pytest.approx(1.0)
    assert result.overall_ratio == pytest.approx(1.0)


def test_specific_minute_partial_coverage():
    result = compute_coverage("30 * * * *")
    assert result.ok
    fc = result.fields["minute"]
    assert fc.covered == 1
    assert fc.total == 60
    assert fc.ratio == pytest.approx(1 / 60)


def test_step_minute_coverage():
    result = compute_coverage("*/15 * * * *")
    assert result.ok
    fc = result.fields["minute"]
    # 0, 15, 30, 45
    assert fc.covered == 4
    assert fc.values == [0, 15, 30, 45]


def test_range_hour_coverage():
    result = compute_coverage("0 9-17 * * *")
    assert result.ok
    fc = result.fields["hour"]
    assert fc.covered == 9  # 9,10,11,12,13,14,15,16,17
    assert fc.total == 24


def test_list_month_coverage():
    result = compute_coverage("0 0 1 1,6,12 *")
    assert result.ok
    fc = result.fields["month"]
    assert fc.covered == 3
    assert fc.values == [1, 6, 12]


def test_overall_ratio_is_average_of_fields():
    result = compute_coverage("0 0 1 1 0")
    assert result.ok
    ratios = [f.ratio for f in result.fields.values()]
    expected = sum(ratios) / len(ratios)
    assert result.overall_ratio == pytest.approx(expected)


def test_invalid_expression_returns_error():
    result = compute_coverage("99 * * * *")
    assert not result.ok
    assert result.error
    assert result.fields == {}


def test_to_dict_keys():
    result = compute_coverage("* * * * *")
    d = result.to_dict()
    assert "expression" in d
    assert "ok" in d
    assert "overall_ratio" in d
    assert "fields" in d
    assert "minute" in d["fields"]


# ---------------------------------------------------------------------------
# formatters
# ---------------------------------------------------------------------------

def test_format_plain_contains_expression():
    result = compute_coverage("*/5 * * * *")
    out = format_coverage_plain(result)
    assert "*/5 * * * *" in out


def test_format_plain_contains_overall():
    result = compute_coverage("*/5 * * * *")
    out = format_coverage_plain(result)
    assert "Overall" in out


def test_format_plain_error():
    result = compute_coverage("bad expression")
    out = format_coverage_plain(result)
    assert "ERROR" in out


def test_format_json_is_valid():
    result = compute_coverage("0 12 * * 1")
    out = format_coverage_json(result)
    data = json.loads(out)
    assert data["ok"] is True
    assert "fields" in data


def test_format_dispatch_plain():
    result = compute_coverage("* * * * *")
    assert format_coverage(result, fmt="plain") == format_coverage_plain(result)


def test_format_dispatch_json():
    result = compute_coverage("* * * * *")
    assert format_coverage(result, fmt="json") == format_coverage_json(result)
