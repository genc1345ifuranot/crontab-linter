"""Tests for crontab_linter.overlap."""
from __future__ import annotations

import datetime
import pytest

from crontab_linter.overlap import find_overlaps, OverlapPair, OverlapResult

_START = datetime.datetime(2024, 1, 15, 0, 0, 0)


def test_no_overlaps_different_hours():
    result = find_overlaps(["0 6 * * *", "0 18 * * *"], start=_START, minutes=1440)
    assert not result.has_overlaps
    assert result.pairs == []


def test_identical_expressions_overlap():
    result = find_overlaps(["30 9 * * *", "30 9 * * *"], start=_START, minutes=1440)
    assert result.has_overlaps
    assert len(result.pairs) == 1
    assert result.pairs[0].expr_a == "30 9 * * *"
    assert result.pairs[0].expr_b == "30 9 * * *"


def test_sample_times_are_datetime_objects():
    result = find_overlaps(["* * * * *", "* * * * *"], start=_START, minutes=10)
    assert result.has_overlaps
    for t in result.pairs[0].sample_times:
        assert isinstance(t, datetime.datetime)


def test_sample_times_capped_at_five():
    result = find_overlaps(["* * * * *", "* * * * *"], start=_START, minutes=60)
    assert len(result.pairs[0].sample_times) <= 5


def test_invalid_expression_recorded_in_errors():
    result = find_overlaps(["not_a_cron", "0 6 * * *"], start=_START, minutes=60)
    assert any("not_a_cron" in e for e in result.errors)


def test_invalid_expression_skipped_in_pairs():
    result = find_overlaps(["bad expr", "0 6 * * *"], start=_START, minutes=60)
    assert not result.has_overlaps


def test_three_expressions_two_pairs_overlap():
    # all fire every minute — 3 choose 2 = 3 pairs
    result = find_overlaps(["* * * * *", "* * * * *", "* * * * *"], start=_START, minutes=5)
    assert len(result.pairs) == 3


def test_to_dict_structure():
    result = find_overlaps(["0 12 * * *", "0 12 * * *"], start=_START, minutes=1440)
    d = result.to_dict()
    assert "has_overlaps" in d
    assert "pairs" in d
    assert "errors" in d
    assert isinstance(d["pairs"], list)


def test_pair_to_dict_contains_iso_times():
    result = find_overlaps(["0 0 * * *", "0 0 * * *"], start=_START, minutes=1440)
    pair_dict = result.pairs[0].to_dict()
    assert "expr_a" in pair_dict
    assert "expr_b" in pair_dict
    assert all(isinstance(t, str) for t in pair_dict["sample_times"])


def test_requires_at_least_two_expressions_silently():
    # single expression — no pairs possible
    result = find_overlaps(["0 6 * * *"], start=_START, minutes=60)
    assert not result.has_overlaps
    assert result.pairs == []
