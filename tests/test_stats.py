"""Tests for crontab_linter.stats and stats_formatter."""
import json
import pytest
from crontab_linter.stats import compute_stats
from crontab_linter.stats_formatter import format_stats_plain, format_stats_json, format_stats

VALID = ["0 9 * * 1", "*/5 * * * *", "0 0 1 1 *"]
INVALID = ["99 * * * *", "0 25 * * *"]
MIXED = VALID + INVALID


def test_total_counts_non_blank():
    r = compute_stats(MIXED)
    assert r.total == len(MIXED)


def test_valid_count():
    r = compute_stats(VALID)
    assert r.valid == 3
    assert r.invalid == 0


def test_invalid_count():
    r = compute_stats(INVALID)
    assert r.invalid == 2
    assert r.valid == 0


def test_skips_blank_and_comment_lines():
    r = compute_stats(["  ", "# comment", "0 9 * * 1"])
    assert r.total == 1


def test_preset_counted():
    r = compute_stats(["@daily", "@weekly"])
    assert r.preset_count == 2
    assert r.valid == 2


def test_invalid_rate():
    r = compute_stats(MIXED)
    assert r.invalid_rate == round(2 / 5, 4)


def test_warning_rate_every_minute():
    r = compute_stats(["* * * * *"])
    assert r.with_warnings >= 1
    assert r.warning_rate > 0


def test_field_frequency_keys():
    r = compute_stats(VALID)
    assert set(r.field_frequency.keys()) == {"minute", "hour", "day_of_month", "month", "day_of_week"}


def test_field_frequency_values():
    r = compute_stats(["0 9 * * 1", "0 9 * * 2"])
    assert r.field_frequency["hour"].get("9", 0) == 2


def test_format_plain_contains_totals():
    r = compute_stats(VALID)
    out = format_stats_plain(r)
    assert "Total" in out
    assert "Valid" in out


def test_format_json_parses():
    r = compute_stats(VALID)
    data = json.loads(format_stats_json(r))
    assert data["total"] == 3
    assert "field_frequency" in data


def test_format_dispatch_plain():
    r = compute_stats(VALID)
    assert format_stats(r, "plain") == format_stats_plain(r)


def test_format_dispatch_json():
    r = compute_stats(VALID)
    assert format_stats(r, "json") == format_stats_json(r)
