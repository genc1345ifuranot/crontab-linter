import pytest
from pathlib import Path
from crontab_linter.remind import add_reminder, get_reminder, remove_reminder, list_reminders


@pytest.fixture
def rfile(tmp_path):
    return tmp_path / "reminders.json"


def test_add_and_get(rfile):
    add_reminder("0 9 * * 1", "Weekly standup", path=rfile)
    entry = get_reminder("0 9 * * 1", path=rfile)
    assert entry is not None
    assert entry.message == "Weekly standup"


def test_get_missing_returns_none(rfile):
    assert get_reminder("* * * * *", path=rfile) is None


def test_overwrite_existing(rfile):
    add_reminder("0 9 * * 1", "Old", path=rfile)
    add_reminder("0 9 * * 1", "New", path=rfile)
    assert get_reminder("0 9 * * 1", path=rfile).message == "New"
    assert len(list_reminders(path=rfile)) == 1


def test_tags_stored(rfile):
    add_reminder("*/5 * * * *", "Every 5 min", tags=["frequent", "monitoring"], path=rfile)
    entry = get_reminder("*/5 * * * *", path=rfile)
    assert "frequent" in entry.tags
    assert "monitoring" in entry.tags


def test_remove_existing(rfile):
    add_reminder("0 0 * * *", "Daily midnight", path=rfile)
    assert remove_reminder("0 0 * * *", path=rfile) is True
    assert get_reminder("0 0 * * *", path=rfile) is None


def test_remove_missing_returns_false(rfile):
    assert remove_reminder("0 0 * * *", path=rfile) is False


def test_list_empty(rfile):
    assert list_reminders(path=rfile) == []


def test_list_multiple(rfile):
    add_reminder("0 9 * * 1", "A", path=rfile)
    add_reminder("0 10 * * 2", "B", path=rfile)
    assert len(list_reminders(path=rfile)) == 2


def test_to_dict_roundtrip(rfile):
    e = add_reminder("0 9 * * 1", "Test", tags=["x"], path=rfile)
    d = e.to_dict()
    assert d["expression"] == "0 9 * * 1"
    assert d["message"] == "Test"
    assert d["tags"] == ["x"]
