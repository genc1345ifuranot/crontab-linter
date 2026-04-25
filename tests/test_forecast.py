"""Tests for crontab_linter.forecast and forecast_formatter."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from unittest.mock import patch

import pytest

from crontab_linter.forecast import (
    ForecastEntry,
    ForecastResult,
    _ordinal,
    compute_forecast,
)
from crontab_linter.forecast_formatter import (
    format_forecast,
    format_forecast_json,
    format_forecast_plain,
)
from crontab_linter.parser import parse

_AFTER = datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc)


def _expr(s: str):
    return parse(s)


# ---------------------------------------------------------------------------
# _ordinal helper
# ---------------------------------------------------------------------------

def test_ordinal_first_ten():
    assert _ordinal(1) == "1st"
    assert _ordinal(2) == "2nd"
    assert _ordinal(3) == "3rd"
    assert _ordinal(4) == "4th"
    assert _ordinal(10) == "10th"


def test_ordinal_beyond_ten():
    assert _ordinal(11) == "11th"
    assert _ordinal(21) == "21st"
    assert _ordinal(22) == "22nd"
    assert _ordinal(23) == "23rd"


# ---------------------------------------------------------------------------
# compute_forecast
# ---------------------------------------------------------------------------

def test_forecast_returns_correct_count():
    result = compute_forecast(_expr("0 * * * *"), count=3, tz_name="UTC", after=_AFTER)
    assert result.ok
    assert len(result.entries) == 3


def test_forecast_entries_are_ordered():
    result = compute_forecast(_expr("0 * * * *"), count=5, tz_name="UTC", after=_AFTER)
    dts = [e.dt for e in result.entries]
    assert dts == sorted(dts)


def test_forecast_labels_are_ordinals():
    result = compute_forecast(_expr("0 * * * *"), count=3, tz_name="UTC", after=_AFTER)
    assert result.entries[0].label == "1st run"
    assert result.entries[1].label == "2nd run"
    assert result.entries[2].label == "3rd run"


def test_forecast_error_on_bad_timezone():
    result = compute_forecast(
        _expr("* * * * *"), count=3, tz_name="Not/ATimezone", after=_AFTER
    )
    assert not result.ok
    assert result.error is not None


def test_forecast_to_dict_keys():
    result = compute_forecast(_expr("0 0 * * *"), count=2, tz_name="UTC", after=_AFTER)
    d = result.to_dict()
    assert {"expression", "timezone", "ok", "error", "entries"} == set(d.keys())


def test_forecast_entry_to_dict():
    dt = datetime(2024, 6, 1, 12, 0, tzinfo=timezone.utc)
    entry = ForecastEntry(dt=dt, label="1st run")
    d = entry.to_dict()
    assert d["label"] == "1st run"
    assert "2024-06-01" in d["datetime"]


# ---------------------------------------------------------------------------
# formatters
# ---------------------------------------------------------------------------

def test_format_plain_contains_expression():
    result = compute_forecast(_expr("0 9 * * 1"), count=2, tz_name="UTC", after=_AFTER)
    out = format_forecast_plain(result)
    assert "0 9 * * 1" in out


def test_format_plain_shows_timezone():
    result = compute_forecast(_expr("0 9 * * 1"), count=2, tz_name="UTC", after=_AFTER)
    out = format_forecast_plain(result)
    assert "UTC" in out


def test_format_plain_shows_ordinal_labels():
    result = compute_forecast(_expr("0 * * * *"), count=2, tz_name="UTC", after=_AFTER)
    out = format_forecast_plain(result)
    assert "1st run" in out
    assert "2nd run" in out


def test_format_plain_error_shown():
    result = ForecastResult(expression="* * * * *", timezone="Bad/Zone", error="unknown timezone")
    out = format_forecast_plain(result)
    assert "Error" in out
    assert "unknown timezone" in out


def test_format_json_valid():
    result = compute_forecast(_expr("0 0 * * *"), count=2, tz_name="UTC", after=_AFTER)
    out = format_forecast_json(result)
    data = json.loads(out)
    assert data["ok"] is True
    assert len(data["entries"]) == 2


def test_format_dispatch_json():
    result = compute_forecast(_expr("0 0 * * *"), count=1, tz_name="UTC", after=_AFTER)
    out = format_forecast(result, fmt="json")
    assert json.loads(out)["ok"] is True


def test_format_dispatch_plain_default():
    result = compute_forecast(_expr("0 0 * * *"), count=1, tz_name="UTC", after=_AFTER)
    out = format_forecast(result)
    assert "Expression" in out
