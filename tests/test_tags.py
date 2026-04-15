"""Tests for crontab_linter/tags.py"""

from __future__ import annotations

import pytest

from crontab_linter.tags import (
    TagEntry,
    get_by_tag,
    list_tags,
    remove_tag,
    tag_expression,
)


@pytest.fixture()
def tag_file(tmp_path):
    return str(tmp_path / "tags.json")


def test_tag_new_expression(tag_file):
    entry = tag_expression("0 * * * *", ["hourly", "prod"], path=tag_file)
    assert entry.expression == "0 * * * *"
    assert "hourly" in entry.tags
    assert "prod" in entry.tags


def test_tag_stores_note(tag_file):
    entry = tag_expression("0 0 * * *", ["daily"], note="midnight run", path=tag_file)
    assert entry.note == "midnight run"


def test_tag_updates_existing_expression(tag_file):
    tag_expression("0 * * * *", ["hourly"], path=tag_file)
    updated = tag_expression("0 * * * *", ["prod"], path=tag_file)
    assert "hourly" in updated.tags
    assert "prod" in updated.tags


def test_tag_deduplicates_tags(tag_file):
    tag_expression("0 * * * *", ["hourly"], path=tag_file)
    updated = tag_expression("0 * * * *", ["hourly", "hourly"], path=tag_file)
    assert updated.tags.count("hourly") == 1


def test_list_tags_empty(tag_file):
    assert list_tags(path=tag_file) == []


def test_list_tags_returns_all(tag_file):
    tag_expression("0 * * * *", ["hourly"], path=tag_file)
    tag_expression("0 0 * * *", ["daily"], path=tag_file)
    entries = list_tags(path=tag_file)
    assert len(entries) == 2


def test_get_by_tag_returns_matching(tag_file):
    tag_expression("0 * * * *", ["hourly", "prod"], path=tag_file)
    tag_expression("0 0 * * *", ["daily", "prod"], path=tag_file)
    tag_expression("*/5 * * * *", ["frequent"], path=tag_file)
    results = get_by_tag("prod", path=tag_file)
    exprs = [e.expression for e in results]
    assert "0 * * * *" in exprs
    assert "0 0 * * *" in exprs
    assert "*/5 * * * *" not in exprs


def test_get_by_tag_no_match(tag_file):
    tag_expression("0 * * * *", ["hourly"], path=tag_file)
    assert get_by_tag("nonexistent", path=tag_file) == []


def test_remove_tag_success(tag_file):
    tag_expression("0 * * * *", ["hourly", "prod"], path=tag_file)
    result = remove_tag("0 * * * *", "prod", path=tag_file)
    assert result is not None
    assert "prod" not in result.tags
    assert "hourly" in result.tags


def test_remove_tag_missing_expression(tag_file):
    result = remove_tag("0 * * * *", "prod", path=tag_file)
    assert result is None


def test_entry_roundtrip():
    entry = TagEntry(expression="*/10 * * * *", tags=["frequent", "dev"], note="test")
    restored = TagEntry.from_dict(entry.to_dict())
    assert restored.expression == entry.expression
    assert restored.tags == entry.tags
    assert restored.note == entry.note


def test_tags_persisted_across_loads(tag_file):
    tag_expression("0 * * * *", ["hourly"], path=tag_file)
    entries = list_tags(path=tag_file)
    assert len(entries) == 1
    assert entries[0].expression == "0 * * * *"
