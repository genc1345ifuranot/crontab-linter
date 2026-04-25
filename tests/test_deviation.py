"""Tests for crontab_linter.deviation and deviation_formatter."""
import json
import pytest

from crontab_linter.deviation import compute_deviation, DeviationResult, FieldDeviation
from crontab_linter.deviation_formatter import format_deviation_plain, format_deviation_json, format_deviation


# ---------------------------------------------------------------------------
# compute_deviation
# ---------------------------------------------------------------------------

def test_identical_expressions_no_deviation():
    r = compute_deviation("0 9 * * 1", "0 9 * * 1")
    assert r.ok
    assert not r.has_deviation
    assert r.deviation_score == 0


def test_single_field_changed():
    r = compute_deviation("0 9 * * 1", "0 10 * * 1")
    assert r.ok
    assert r.has_deviation
    assert r.deviation_score == 1


def test_changed_field_recorded():
    r = compute_deviation("0 9 * * 1", "0 10 * * 1")
    hour_fd = next(f for f in r.fields if f.name == "hour")
    assert hour_fd.changed
    assert hour_fd.baseline == "9"
    assert hour_fd.candidate == "10"


def test_unchanged_fields_not_marked():
    r = compute_deviation("0 9 * * 1", "0 9 * * 2")
    minute_fd = next(f for f in r.fields if f.name == "minute")
    assert not minute_fd.changed


def test_multiple_fields_changed():
    r = compute_deviation("0 9 * * 1", "30 18 1 6 5")
    assert r.deviation_score == 5


def test_invalid_baseline_returns_error():
    r = compute_deviation("99 9 * * 1", "0 9 * * 1")
    assert not r.ok
    assert any("baseline" in e for e in r.errors)


def test_invalid_candidate_returns_error():
    r = compute_deviation("0 9 * * 1", "0 99 * * 1")
    assert not r.ok
    assert any("candidate" in e for e in r.errors)


def test_unparseable_baseline_returns_error():
    r = compute_deviation("not a cron", "0 9 * * 1")
    assert not r.ok


def test_to_dict_keys():
    r = compute_deviation("0 9 * * 1", "0 10 * * 1")
    d = r.to_dict()
    assert "baseline" in d
    assert "candidate" in d
    assert "deviation_score" in d
    assert "fields" in d
    assert "ok" in d


def test_field_deviation_to_dict():
    fd = FieldDeviation(name="minute", baseline="0", candidate="5", changed=True)
    d = fd.to_dict()
    assert d["field"] == "minute"
    assert d["changed"] is True


# ---------------------------------------------------------------------------
# formatters
# ---------------------------------------------------------------------------

def test_plain_no_deviation_message():
    r = compute_deviation("0 9 * * 1", "0 9 * * 1")
    out = format_deviation_plain(r)
    assert "equivalent" in out


def test_plain_shows_changed_field():
    r = compute_deviation("0 9 * * 1", "0 10 * * 1")
    out = format_deviation_plain(r)
    assert "hour" in out
    assert "->" in out


def test_plain_shows_score():
    r = compute_deviation("0 9 * * 1", "0 10 * * 1")
    out = format_deviation_plain(r)
    assert "1" in out


def test_plain_shows_errors():
    r = compute_deviation("99 9 * * 1", "0 9 * * 1")
    out = format_deviation_plain(r)
    assert "Errors" in out or "error" in out.lower()


def test_json_output_is_valid_json():
    r = compute_deviation("0 9 * * 1", "0 10 * * 1")
    out = format_deviation_json(r)
    parsed = json.loads(out)
    assert parsed["deviation_score"] == 1


def test_format_dispatch_plain():
    r = compute_deviation("0 9 * * 1", "0 9 * * 1")
    assert format_deviation(r, fmt="plain") == format_deviation_plain(r)


def test_format_dispatch_json():
    r = compute_deviation("0 9 * * 1", "0 9 * * 1")
    assert format_deviation(r, fmt="json") == format_deviation_json(r)
