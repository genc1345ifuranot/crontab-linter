import json
import pytest
from crontab_linter.duplicate import find_duplicates, DuplicateGroup, DuplicateResult
from crontab_linter.duplicate_formatter import format_duplicate_plain, format_duplicate_json, format_duplicate


def test_no_duplicates():
    result = find_duplicates({"a": "0 * * * *", "b": "5 * * * *"})
    assert not result.has_duplicates()
    assert result.total_duplicates() == 0
    assert result.groups == []


def test_single_duplicate_group():
    result = find_duplicates({"a": "0 * * * *", "b": "0 * * * *"})
    assert result.has_duplicates()
    assert len(result.groups) == 1
    assert result.groups[0].count() == 2
    assert set(result.groups[0].sources) == {"a", "b"}


def test_total_duplicates_count():
    result = find_duplicates({"a": "0 * * * *", "b": "0 * * * *", "c": "0 * * * *"})
    assert result.total_duplicates() == 2


def test_multiple_groups():
    entries = {
        "a": "0 * * * *",
        "b": "0 * * * *",
        "c": "5 0 * * *",
        "d": "5 0 * * *",
    }
    result = find_duplicates(entries)
    assert len(result.groups) == 2
    assert result.total_duplicates() == 2


def test_whitespace_normalized():
    result = find_duplicates({"a": "0 * * * *", "b": "  0 * * * *  "})
    assert result.has_duplicates()


def test_to_dict():
    result = find_duplicates({"a": "0 * * * *", "b": "0 * * * *"})
    d = result.to_dict()
    assert d["has_duplicates"] is True
    assert d["total_duplicates"] == 1
    assert len(d["groups"]) == 1
    assert d["groups"][0]["count"] == 2


def test_format_plain_no_duplicates():
    result = find_duplicates({"a": "0 * * * *"})
    out = format_duplicate_plain(result)
    assert "No duplicate" in out


def test_format_plain_with_duplicates():
    result = find_duplicates({"a": "0 * * * *", "b": "0 * * * *"})
    out = format_duplicate_plain(result)
    assert "0 * * * *" in out
    assert "Total redundant" in out


def test_format_json():
    result = find_duplicates({"a": "0 * * * *", "b": "0 * * * *"})
    out = format_duplicate_json(result)
    data = json.loads(out)
    assert data["has_duplicates"] is True


def test_format_dispatch_plain():
    result = find_duplicates({})
    assert format_duplicate(result, fmt="plain") == format_duplicate_plain(result)


def test_format_dispatch_json():
    result = find_duplicates({})
    assert format_duplicate(result, fmt="json") == format_duplicate_json(result)
