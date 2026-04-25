"""Tests for crontab_linter.similarity and similarity_formatter."""
import json
import pytest

from crontab_linter.similarity import compute_similarity, _expand_field, _jaccard
from crontab_linter.similarity_formatter import (
    format_similarity_plain,
    format_similarity_json,
    format_similarity,
)


# ---------------------------------------------------------------------------
# _expand_field helpers
# ---------------------------------------------------------------------------

def test_expand_wildcard_minute():
    assert _expand_field("*", 0, 59) == set(range(60))


def test_expand_specific_value():
    assert _expand_field("5", 0, 59) == {5}


def test_expand_range():
    assert _expand_field("1-3", 0, 59) == {1, 2, 3}


def test_expand_step():
    assert _expand_field("*/15", 0, 59) == {0, 15, 30, 45}


def test_expand_list():
    assert _expand_field("1,2,3", 0, 59) == {1, 2, 3}


# ---------------------------------------------------------------------------
# _jaccard
# ---------------------------------------------------------------------------

def test_jaccard_identical():
    assert _jaccard({1, 2, 3}, {1, 2, 3}) == 1.0


def test_jaccard_disjoint():
    assert _jaccard({1}, {2}) == 0.0


def test_jaccard_partial():
    score = _jaccard({1, 2}, {2, 3})
    assert abs(score - 1 / 3) < 1e-9


def test_jaccard_both_empty():
    assert _jaccard(set(), set()) == 1.0


# ---------------------------------------------------------------------------
# compute_similarity
# ---------------------------------------------------------------------------

def test_identical_expressions_score_one():
    r = compute_similarity("* * * * *", "* * * * *")
    assert r.score == pytest.approx(1.0)
    assert r.valid_a and r.valid_b
    assert not r.errors


def test_completely_different_fixed_fields():
    r = compute_similarity("0 0 1 1 0", "30 12 15 6 5")
    assert r.score < 0.2


def test_same_minute_different_hour():
    r = compute_similarity("0 * * * *", "0 12 * * *")
    # minute field identical (score 1.0), hour field partial
    assert r.field_scores[0] == pytest.approx(1.0)
    assert r.field_scores[1] < 1.0


def test_invalid_expression_returns_errors():
    r = compute_similarity("99 * * * *", "* * * * *")
    assert not r.valid_a
    assert r.errors
    assert r.score == pytest.approx(0.0)


def test_field_scores_length():
    r = compute_similarity("*/5 * * * *", "*/10 * * * *")
    assert len(r.field_scores) == 5


def test_to_dict_keys():
    r = compute_similarity("* * * * *", "* * * * *")
    d = r.to_dict()
    assert set(d.keys()) == {
        "expr_a", "expr_b", "score", "field_scores", "valid_a", "valid_b", "errors"
    }


# ---------------------------------------------------------------------------
# formatter
# ---------------------------------------------------------------------------

def test_plain_contains_score():
    r = compute_similarity("* * * * *", "* * * * *")
    out = format_similarity_plain(r)
    assert "100.0%" in out


def test_plain_contains_field_names():
    r = compute_similarity("* * * * *", "* * * * *")
    out = format_similarity_plain(r)
    for name in ["minute", "hour", "day-of-month", "month", "day-of-week"]:
        assert name in out


def test_json_format_is_valid_json():
    r = compute_similarity("0 12 * * 1", "0 12 * * 1")
    out = format_similarity_json(r)
    data = json.loads(out)
    assert data["score"] == pytest.approx(1.0)


def test_format_dispatch_plain():
    r = compute_similarity("* * * * *", "* * * * *")
    assert format_similarity(r, fmt="plain") == format_similarity_plain(r)


def test_format_dispatch_json():
    r = compute_similarity("* * * * *", "* * * * *")
    assert format_similarity(r, fmt="json") == format_similarity_json(r)


def test_plain_shows_errors_for_invalid():
    r = compute_similarity("99 * * * *", "* * * * *")
    out = format_similarity_plain(r)
    assert "Errors" in out
