"""Tests for crontab_linter.schedule and crontab_linter.schedule_formatter."""

from __future__ import annotations

from datetime import datetime

import pytz
import pytest

from crontab_linter.parser import CronExpression
from crontab_linter.schedule import ScheduleResult, _matches, next_runs
from crontab_linter.schedule_formatter import format_schedule

_ANCHOR = datetime(2024, 3, 1, 12, 0, tzinfo=pytz.UTC)  # Friday


def _parse(raw: str) -> CronExpression:
    return CronExpression.parse(raw)


# ---------------------------------------------------------------------------
# _matches
# ---------------------------------------------------------------------------

def test_matches_wildcard():
    expr = _parse("* * * * *")
    assert _matches(_ANCHOR, expr)


def test_matches_specific_minute():
    expr = _parse("0 12 * * *")
    assert _matches(_ANCHOR, expr)
    not_matching = _ANCHOR.replace(minute=1)
    assert not _matches(not_matching, expr)


def test_matches_step():
    expr = _parse("*/15 * * * *")
    for m in (0, 15, 30, 45):
        assert _matches(_ANCHOR.replace(minute=m), expr)
    assert not _matches(_ANCHOR.replace(minute=7), expr)


def test_matches_range():
    expr = _parse("0 9-17 * * *")
    assert _matches(_ANCHOR.replace(hour=9), expr)
    assert _matches(_ANCHOR.replace(hour=17), expr)
    assert not _matches(_ANCHOR.replace(hour=8), expr)


def test_matches_list():
    expr = _parse("0 0 1,15 * *")
    assert _matches(_ANCHOR.replace(day=1, hour=0, minute=0), expr)
    assert _matches(_ANCHOR.replace(day=15, hour=0, minute=0), expr)
    assert not _matches(_ANCHOR.replace(day=10, hour=0, minute=0), expr)


# ---------------------------------------------------------------------------
# next_runs
# ---------------------------------------------------------------------------

def test_next_runs_count():
    expr = _parse("0 * * * *")
    result = next_runs(expr, timezone="UTC", count=3, start=_ANCHOR)
    assert len(result.next_runs) == 3


def test_next_runs_values_are_future():
    expr = _parse("* * * * *")
    result = next_runs(expr, timezone="UTC", count=5, start=_ANCHOR)
    for dt in result.next_runs:
        assert dt > _ANCHOR


def test_next_runs_unknown_timezone():
    expr = _parse("* * * * *")
    result = next_runs(expr, timezone="Mars/Olympus", count=1)
    assert result.error is not None
    assert "Mars/Olympus" in result.error
    assert result.next_runs == []


def test_next_runs_named_timezone():
    expr = _parse("0 9 * * *")
    tz = pytz.timezone("America/New_York")
    start = datetime(2024, 6, 1, 8, 59, tzinfo=tz)
    result = next_runs(expr, timezone="America/New_York", count=1, start=start)
    assert len(result.next_runs) == 1
    assert result.next_runs[0].hour == 9
    assert result.next_runs[0].minute == 0


# ---------------------------------------------------------------------------
# format_schedule
# ---------------------------------------------------------------------------

def test_format_plain_contains_expression():
    expr = _parse("0 12 * * *")
    result = next_runs(expr, timezone="UTC", count=2, start=_ANCHOR)
    out = format_schedule(result, fmt="plain")
    assert "0 12 * * *" in out
    assert "UTC" in out


def test_format_json_valid():
    import json
    expr = _parse("0 12 * * *")
    result = next_runs(expr, timezone="UTC", count=2, start=_ANCHOR)
    out = format_schedule(result, fmt="json")
    data = json.loads(out)
    assert data["expression"] == "0 12 * * *"
    assert len(data["next_runs"]) == 2


def test_format_plain_error():
    result = ScheduleResult(expression="* * * * *", timezone="Bad/Zone", error="Unknown timezone")
    out = format_schedule(result, fmt="plain")
    assert "Error" in out


def test_format_json_error():
    import json
    result = ScheduleResult(expression="* * * * *", timezone="Bad/Zone", error="Unknown timezone")
    out = format_schedule(result, fmt="json")
    data = json.loads(out)
    assert "error" in data
