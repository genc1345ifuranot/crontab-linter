import pytest
from crontab_linter.normalize import normalize, NormalizeResult


def test_basic_wildcard_unchanged():
    r = normalize("* * * * *")
    assert r.ok
    assert r.normalized == "* * * * *"
    assert r.was_preset is False


def test_leading_zeros_stripped():
    r = normalize("05 08 01 01 0")
    assert r.ok
    assert r.normalized == "5 8 1 1 0"


def test_step_value_normalized():
    r = normalize("*/05 * * * *")
    assert r.ok
    assert r.normalized == "*/5 * * * *"


def test_range_normalized():
    r = normalize("01-05 * * * *")
    assert r.ok
    assert r.normalized == "1-5 * * * *"


def test_list_normalized():
    r = normalize("01,02,03 * * * *")
    assert r.ok
    assert r.normalized == "1,2,3 * * * *"


def test_month_alias_uppercased():
    r = normalize("0 0 * jan *")
    assert r.ok
    assert "JAN" in r.normalized


def test_dow_alias_uppercased():
    r = normalize("0 0 * * mon")
    assert r.ok
    assert "MON" in r.normalized


def test_preset_resolved_and_normalized():
    r = normalize("@daily")
    assert r.ok
    assert r.was_preset is True
    assert r.normalized == "0 0 * * *"


def test_preset_yearly():
    r = normalize("@yearly")
    assert r.ok
    assert r.was_preset is True
    assert r.normalized == "0 0 1 1 *"


def test_invalid_expression_returns_error():
    r = normalize("99 * * * *")
    assert not r.ok
    assert r.normalized is None
    assert r.error is not None


def test_to_dict_keys():
    r = normalize("* * * * *")
    d = r.to_dict()
    assert set(d.keys()) == {"original", "normalized", "was_preset", "error"}


def test_original_preserved():
    expr = "  05 08 * * *  "
    r = normalize(expr)
    assert r.original == expr.strip()
