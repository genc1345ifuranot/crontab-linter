import pytest
from crontab_linter.classify import classify


def test_every_minute():
    r = classify("* * * * *")
    assert r.category == "every-minute"
    assert r.valid is True
    assert r.error is None


def test_hourly():
    r = classify("30 * * * *")
    assert r.category == "hourly"
    assert "30" in r.description


def test_daily():
    r = classify("0 9 * * *")
    assert r.category == "daily"
    assert r.frequency == "daily"
    assert "9" in r.description


def test_weekly():
    r = classify("0 8 * * 1")
    assert r.category == "weekly"
    assert r.frequency == "weekly"


def test_monthly():
    r = classify("0 6 1 * *")
    assert r.category == "monthly"
    assert r.frequency == "monthly"
    assert "1" in r.description


def test_yearly():
    r = classify("0 0 1 1 *")
    assert r.category == "yearly"
    assert r.frequency == "yearly"


def test_interval():
    r = classify("*/15 * * * *")
    assert r.category == "interval"
    assert r.frequency == "every-15-minutes"


def test_custom():
    r = classify("0 9-17 * * 1-5")
    assert r.category == "custom"
    assert r.valid is True


def test_invalid_expression():
    r = classify("99 * * * *")
    assert r.valid is False
    assert r.category == "unknown"
    assert r.error is not None


def test_to_dict_keys():
    r = classify("0 0 * * *")
    d = r.to_dict()
    assert set(d.keys()) == {"expression", "category", "frequency", "description", "valid", "error"}


def test_to_dict_invalid():
    r = classify("bad expression")
    d = r.to_dict()
    assert d["valid"] is False
    assert d["error"] is not None
