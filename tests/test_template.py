"""Tests for crontab_linter.template module."""
import pytest

from crontab_linter.template import (
    TemplateEntry,
    delete_template,
    get_template,
    list_templates,
    save_template,
)


@pytest.fixture
def tpl_file(tmp_path):
    return str(tmp_path / "templates.json")


def test_save_and_get(tpl_file):
    entry = save_template("daily_backup", "0 2 * * *", path=tpl_file)
    assert entry.name == "daily_backup"
    assert entry.expression == "0 2 * * *"

    result = get_template("daily_backup", path=tpl_file)
    assert result is not None
    assert result.expression == "0 2 * * *"


def test_get_missing_returns_none(tpl_file):
    assert get_template("nonexistent", path=tpl_file) is None


def test_overwrite_template(tpl_file):
    save_template("job", "0 1 * * *", path=tpl_file)
    save_template("job", "0 3 * * *", path=tpl_file)
    result = get_template("job", path=tpl_file)
    assert result.expression == "0 3 * * *"


def test_save_with_description_and_tags(tpl_file):
    save_template("weekly", "0 9 * * 1", description="Every Monday 9am", tags=["work", "report"], path=tpl_file)
    result = get_template("weekly", path=tpl_file)
    assert result.description == "Every Monday 9am"
    assert "work" in result.tags
    assert "report" in result.tags


def test_list_empty(tpl_file):
    assert list_templates(path=tpl_file) == []


def test_list_multiple(tpl_file):
    save_template("a", "* * * * *", path=tpl_file)
    save_template("b", "0 0 * * *", path=tpl_file)
    entries = list_templates(path=tpl_file)
    assert len(entries) == 2
    names = {e.name for e in entries}
    assert names == {"a", "b"}


def test_delete_existing(tpl_file):
    save_template("temp", "*/5 * * * *", path=tpl_file)
    removed = delete_template("temp", path=tpl_file)
    assert removed is True
    assert path=tpl_file) is None


def test_delete_nonexistent(tpl_file):
    assert delete_template("ghost", path=tpl_file) is False


def test_to_dict_round_trip():
    entry = TemplateEntry(name="x", expression="0 12 * * *", description="noon", tags=["daily"])
    d = entry.to_dict()
    restored = TemplateEntry.from_dict(d)
    assert restored.name == entry.name
    assert restored.expression == entry.expression
    assert restored.description == entry.description
    assert restored.tags == entry.tags


def test_save_default_tags_empty(tpl_file):
    entry = save_template("no_tags", "0 0 1 * *", path=tpl_file)
    assert entry.tags == []
