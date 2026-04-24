"""Tests for crontab_linter.conflict and conflict_formatter."""
from __future__ import annotations

import datetime
import json

import pytest

from crontab_linter.conflict import find_conflicts
from crontab_linter.conflict_formatter import format_conflict


START = datetime.datetime(2024, 1, 1, 0, 0)


# ---------------------------------------------------------------------------
# find_conflicts
# ---------------------------------------------------------------------------

def test_identical_expressions_have_conflicts():
    result = find_conflicts("* * * * *", "* * * * *", window_hours=1, start=START)
    assert result.valid
    assert result.has_conflict
    assert len(result.overlap_times) == 10  # capped at default max_overlaps


def test_non_overlapping_hours():
    # Runs at 06:00 vs 18:00 — no overlap in a 1-hour window starting at midnight
    result = find_conflicts("0 6 * * *", "0 18 * * *", window_hours=1, start=START)
    assert result.valid
    assert not result.has_conflict
    assert result.overlap_times == []


def test_same_minute_overlap():
    # Both fire at minute 30 of every hour
    result = find_conflicts("30 * * * *", "30 * * * *", window_hours=2, start=START)
    assert result.valid
    assert result.has_conflict
    # Expect 2 overlaps in 2 hours (minute 30 of hour 0 and hour 1)
    assert len(result.overlap_times) == 2


def test_different_minutes_no_overlap():
    result = find_conflicts("0 * * * *", "30 * * * *", window_hours=1, start=START)
    assert result.valid
    assert not result.has_conflict


def test_invalid_expr_a():
    result = find_conflicts("99 * * * *", "* * * * *", start=START)
    assert not result.valid
    assert any("Expression A" in e for e in result.errors)


def test_invalid_expr_b():
    result = find_conflicts("* * * * *", "* * * 13 *", start=START)
    assert not result.valid
    assert any("Expression B" in e for e in result.errors)


def test_max_overlaps_respected():
    result = find_conflicts(
        "* * * * *", "* * * * *",
        window_hours=1, start=START, max_overlaps=5
    )
    assert len(result.overlap_times) == 5


def test_message_no_conflict():
    result = find_conflicts("0 6 * * *", "0 18 * * *", window_hours=1, start=START)
    assert "No conflicts" in result.message


def test_message_with_conflict():
    result = find_conflicts("* * * * *", "* * * * *", window_hours=1, start=START)
    assert "overlapping" in result.message.lower()


# ---------------------------------------------------------------------------
# format_conflict
# ---------------------------------------------------------------------------

def test_format_plain_no_conflict():
    result = find_conflicts("0 6 * * *", "0 18 * * *", window_hours=1, start=START)
    out = format_conflict(result, fmt="plain")
    assert "NO CONFLICT" in out
    assert "Expression A" in out


def test_format_plain_conflict():
    result = find_conflicts("* * * * *", "* * * * *", window_hours=1, start=START)
    out = format_conflict(result, fmt="plain")
    assert "CONFLICT DETECTED" in out
    assert "2024-01-01" in out


def test_format_json_structure():
    result = find_conflicts("30 * * * *", "30 * * * *", window_hours=2, start=START)
    out = format_conflict(result, fmt="json")
    data = json.loads(out)
    assert data["has_conflict"] is True
    assert "overlap_times" in data
    assert data["overlap_count"] == 2


def test_format_plain_invalid():
    result = find_conflicts("99 * * * *", "* * * * *", start=START)
    out = format_conflict(result, fmt="plain")
    assert "INVALID" in out
    assert "Expression A" in out
