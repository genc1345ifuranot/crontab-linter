"""Tests for crontab_linter.interpolate."""
from __future__ import annotations

import pytest

from crontab_linter.interpolate import interpolate, InterpolateResult


def test_no_variables_unchanged():
    r = interpolate("*/5 * * * *", {})
    assert r.interpolated == "*/5 * * * *"
    assert r.ok
    assert r.variables_used == []
    assert r.missing_variables == []


def test_dollar_brace_substitution():
    r = interpolate("${MIN} ${HOUR} * * *", {"MIN": "0", "HOUR": "12"})
    assert r.interpolated == "0 12 * * *"
    assert r.ok
    assert set(r.variables_used) == {"MIN", "HOUR"}


def test_bare_dollar_substitution():
    r = interpolate("$MIN * * * *", {"MIN": "30"})
    assert r.interpolated == "30 * * * *"
    assert r.ok
    assert "MIN" in r.variables_used


def test_missing_variable_reported():
    r = interpolate("${MIN} * * * *", {})
    assert not r.ok
    assert "MIN" in r.missing_variables
    assert "${MIN}" in r.interpolated  # placeholder left intact


def test_partial_substitution():
    r = interpolate("${MIN} ${HOUR} * * *", {"MIN": "5"})
    assert not r.ok
    assert "MIN" in r.variables_used
    assert "HOUR" in r.missing_variables
    assert r.interpolated == "5 ${HOUR} * * *"


def test_none_variables_treated_as_empty():
    r = interpolate("* * * * *", None)
    assert r.ok
    assert r.interpolated == "* * * * *"


def test_duplicate_variable_counted_once():
    r = interpolate("${V} ${V} * * *", {"V": "1"})
    assert r.variables_used.count("V") == 1


def test_to_dict_keys():
    r = interpolate("* * * * *", {})
    d = r.to_dict()
    assert "original" in d
    assert "interpolated" in d
    assert "variables_used" in d
    assert "missing_variables" in d
    assert "ok" in d


def test_original_preserved():
    expr = "${X} * * * *"
    r = interpolate(expr, {"X": "0"})
    assert r.original == expr
