"""Tests for template storage module."""

import pytest

from crontab_linter.template import (
    save_template, get_template, delete_template, list_templates, TemplateEntry
)


@pytest.fixture
def tpl_file(tmp_path):
    return str(tmp_path / "templates.json")


def test_save_and_get(tpl_file):
    save_template("daily", "0 0 * * *", path=tpl_file)
    entry = get_template("daily", path=tpl_file)
    assert entry is not None
    assert entry.expression == "0 0 * * *"


def test_get_missing_returns_none(tpl_file):
    result = get_template("nonexistent", path=tpl_file)
    assert result is None


def test_overwrite_template(tpl_file):
    save_template("t", "0 0 * * *", path=tpl_file)
    save_template("t", "0 12 * * *", path=tpl_file)
    entries = list_templates(path=tpl_file)
    assert len(entries) == 1
    assert entries[0].expression == "0 12 * * *"


def test_save_with_description_and_tags(tpl_file):
    save_template("weekly", "0 0 * * 0", description="Every Sunday",
                  tags=["ops", "weekly"], path=tpl_file)
    entry = get_template("weekly", path=tpl_file)
    assert entry.description == "Every Sunday"
    assert "ops" in entry.tags
    assert "weekly" in entry.tags


def test_delete_existing(tpl_file):
    save_template("to_remove", "* * * * *", path=tpl_file)
    result = delete_template("to_remove", path=tpl_file)
    assert result is True
    assert get_template("to_remove", path=tpl_file) is None


def test_delete_missing_returns_false(tpl_file):
    result = delete_template("ghost", path=tpl_file)
    assert result is False


def test_list_empty(tpl_file):
    assert list_templates(path=tpl_file) == []


def test_list_multiple(tpl_file):
    save_template("a", "0 1 * * *", path=tpl_file)
    save_template("b", "0 2 * * *", path=tpl_file)
    entries = list_templates(path=tpl_file)
    names = [e.name for e in entries]
    assert "a" in names
    assert "b" in names


def test_to_dict_roundtrip():
    entry = TemplateEntry(name="x", expression="0 0 * * *",
                          description="desc", tags=["a", "b"])
    d = entry.to_dict()
    restored = TemplateEntry.from_dict(d)
    assert restored.name == entry.name
    assert restored.expression == entry.expression
    assert restored.description == entry.description
    assert restored.tags == entry.tags
