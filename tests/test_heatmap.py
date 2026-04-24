"""Tests for crontab_linter.heatmap and heatmap_formatter."""
import json
import pytest

from crontab_linter.heatmap import compute_heatmap, _expand_field
from crontab_linter.heatmap_formatter import format_heatmap_plain, format_heatmap_json, format_heatmap


# ---------------------------------------------------------------------------
# _expand_field helpers
# ---------------------------------------------------------------------------

def test_expand_wildcard():
    assert _expand_field("*", 0, 4) == [0, 1, 2, 3, 4]


def test_expand_specific():
    assert _expand_field("5", 0, 59) == [5]


def test_expand_range():
    assert _expand_field("2-4", 0, 59) == [2, 3, 4]


def test_expand_step():
    assert _expand_field("*/15", 0, 59) == [0, 15, 30, 45]


def test_expand_list():
    assert _expand_field("1,3,5", 0, 59) == [1, 3, 5]


# ---------------------------------------------------------------------------
# compute_heatmap
# ---------------------------------------------------------------------------

def test_invalid_expression_returns_errors():
    r = compute_heatmap("99 * * * *")
    assert not r.valid
    assert r.errors
    assert r.total_hits_per_day == 0


def test_every_minute_hits_per_day():
    r = compute_heatmap("* * * * *")
    assert r.valid
    assert r.total_hits_per_day == 60 * 24


def test_hourly_expression_hits_per_day():
    r = compute_heatmap("0 * * * *")
    assert r.valid
    assert r.total_hits_per_day == 24


def test_specific_hour_and_minute():
    r = compute_heatmap("30 9 * * *")
    assert r.valid
    assert r.total_hits_per_day == 1
    assert r.hourly["9"] == 1
    assert r.minutely["30"] == 1
    assert r.hourly["10"] == 0


def test_step_minutes_every_two_hours():
    r = compute_heatmap("*/30 */2 * * *")
    assert r.valid
    # minutes: 0,30 -> 2; hours: 0,2,4,6,8,10,12,14,16,18,20,22 -> 12
    assert r.total_hits_per_day == 2 * 12


def test_hourly_dict_has_all_24_keys():
    r = compute_heatmap("0 * * * *")
    assert set(r.hourly.keys()) == {str(h) for h in range(24)}


def test_minutely_dict_has_all_60_keys():
    r = compute_heatmap("* * * * *")
    assert set(r.minutely.keys()) == {str(m) for m in range(60)}


# ---------------------------------------------------------------------------
# formatters
# ---------------------------------------------------------------------------

def test_plain_contains_expression():
    r = compute_heatmap("0 9 * * 1-5")
    out = format_heatmap_plain(r)
    assert "0 9 * * 1-5" in out


def test_plain_shows_total_hits():
    r = compute_heatmap("0 9 * * *")
    out = format_heatmap_plain(r)
    assert "Total hits/day: 1" in out


def test_plain_invalid_shows_invalid():
    r = compute_heatmap("99 * * * *")
    out = format_heatmap_plain(r)
    assert "INVALID" in out


def test_json_format_is_parseable():
    r = compute_heatmap("*/5 * * * *")
    data = json.loads(format_heatmap_json(r))
    assert data["valid"] is True
    assert "hourly" in data
    assert "minutely" in data


def test_format_dispatch_json():
    r = compute_heatmap("0 0 * * *")
    out = format_heatmap(r, fmt="json")
    assert json.loads(out)["total_hits_per_day"] == 1


def test_format_dispatch_plain():
    r = compute_heatmap("0 0 * * *")
    out = format_heatmap(r, fmt="plain")
    assert "Heatmap for" in out
