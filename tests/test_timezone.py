"""Tests for crontab_linter.timezone module."""

import pytest

from crontab_linter.timezone import (
    TimezoneCheckResult,
    check_dst_ambiguity,
    utc_offset_summary,
    validate_timezone,
)


# ---------------------------------------------------------------------------
# validate_timezone
# ---------------------------------------------------------------------------

def test_validate_known_timezone():
    result = validate_timezone("America/New_York")
    assert isinstance(result, TimezoneCheckResult)
    assert result.valid is True
    assert result.warning is None


def test_validate_utc_timezone():
    result = validate_timezone("UTC")
    assert result.valid is True


def test_validate_unknown_timezone():
    result = validate_timezone("Mars/Olympus_Mons")
    assert result.valid is False
    assert result.warning is not None
    assert "Mars/Olympus_Mons" in result.warning


def test_validate_empty_string():
    result = validate_timezone("")
    assert result.valid is False


# ---------------------------------------------------------------------------
# check_dst_ambiguity
# ---------------------------------------------------------------------------

def test_dst_check_invalid_timezone():
    result = check_dst_ambiguity("Not/AReal_Zone", hour=2)
    assert result.valid is False
    assert result.warning is not None


def test_dst_check_utc_no_warning():
    # UTC never has DST, so any hour should be safe.
    result = check_dst_ambiguity("UTC", hour=2, minute=30)
    assert result.valid is True
    assert result.warning is None


def test_dst_check_safe_hour():
    # Noon is never in a DST gap.
    result = check_dst_ambiguity("America/Chicago", hour=12, minute=0)
    assert result.valid is True


def test_dst_check_returns_info_when_safe():
    result = check_dst_ambiguity("Europe/London", hour=15, minute=0)
    assert result.valid is True
    # Either info or warning may be set; warning must be absent for safe times.
    assert result.warning is None or "gap" in (result.warning or "")


# ---------------------------------------------------------------------------
# utc_offset_summary
# ---------------------------------------------------------------------------

def test_utc_offset_utc():
    summary = utc_offset_summary("UTC")
    assert summary is not None
    assert summary.startswith("UTC")


def test_utc_offset_new_york():
    summary = utc_offset_summary("America/New_York")
    assert summary is not None
    # New York is UTC-4 or UTC-5 depending on DST.
    assert summary.startswith("UTC-")


def test_utc_offset_unknown_timezone():
    summary = utc_offset_summary("Fake/Zone")
    assert summary is None


def test_utc_offset_positive_zone():
    summary = utc_offset_summary("Asia/Tokyo")
    assert summary is not None
    assert summary.startswith("UTC+")
