import pytest
from crontab_linter.summarize import summarize


def test_every_minute():
    r = summarize("* * * * *")
    assert r.valid
    assert r.category == "every-minute"
    assert "every minute" in r.description.lower()


def test_daily():
    r = summarize("30 8 * * *")
    assert r.valid
    assert r.category == "daily"
    assert "8" in r.description
    assert "30" in r.description


def test_weekly():
    r = summarize("0 9 * * 1")
    assert r.valid
    assert r.category == "weekly"
    assert "1" in r.description


def test_monthly():
    r = summarize("0 0 15 * *")
    assert r.valid
    assert r.category == "monthly"
    assert "15" in r.description


def test_yearly():
    r = summarize("0 12 1 1 *")
    assert r.valid
    assert r.category == "yearly"
    assert "1" in r.description


def test_interval_minutes():
    r = summarize("*/15 * * * *")
    assert r.valid
    assert r.category == "interval"
    assert "15" in r.description


def test_interval_hours():
    r = summarize("* */6 * * *")
    assert r.valid
    assert r.category == "interval"
    assert "6" in r.description


def test_custom():
    r = summarize("5 4 * * 1,3")
    assert r.valid
    assert r.category in ("weekly", "custom")


def test_invalid_expression():
    r = summarize("99 * * * *")
    assert not r.valid
    assert r.category == "invalid"
    assert r.error


def test_to_dict_keys():
    r = summarize("0 0 * * *")
    d = r.to_dict()
    assert set(d.keys()) == {"expression", "category", "description", "valid", "error"}


def test_to_dict_invalid():
    r = summarize("bad expression")
    d = r.to_dict()
    assert d["valid"] is False
    assert d["category"] == "invalid"
