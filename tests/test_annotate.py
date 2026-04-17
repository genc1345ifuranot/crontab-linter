"""Tests for annotate module and CLI."""
import argparse
import pytest

from crontab_linter.annotate import add_note, get_notes, list_annotations, remove_note
from crontab_linter.annotate_cli import cmd_add, cmd_get, cmd_list, cmd_remove


@pytest.fixture
def afile(tmp_path):
    return str(tmp_path / "annotations.json")


def _ns(afile, **kw) -> argparse.Namespace:
    defaults = {"annotate_file": afile}
    defaults.update(kw)
    return argparse.Namespace(**defaults)


def test_add_and_get(afile):
    add_note("* * * * *", "runs every minute", path=afile)
    entry = get_notes("* * * * *", path=afile)
    assert entry is not None
    assert "runs every minute" in entry.notes


def test_get_missing_returns_none(afile):
    assert get_notes("0 0 * * *", path=afile) is None


def test_add_deduplicates(afile):
    add_note("0 * * * *", "hourly", path=afile)
    add_note("0 * * * *", "hourly", path=afile)
    entry = get_notes("0 * * * *", path=afile)
    assert entry.notes.count("hourly") == 1


def test_add_multiple_notes(afile):
    add_note("0 0 * * *", "midnight", path=afile)
    add_note("0 0 * * *", "daily reset", path=afile)
    entry = get_notes("0 0 * * *", path=afile)
    assert len(entry.notes) == 2


def test_remove_note(afile):
    add_note("5 4 * * *", "backup", path=afile)
    remove_note("5 4 * * *", "backup", path=afile)
    entry = get_notes("5 4 * * *", path=afile)
    assert entry.notes == []


def test_list_annotations(afile):
    add_note("* * * * *", "note1", path=afile)
    add_note("0 0 * * *", "note2", path=afile)
    all_entries = list_annotations(path=afile)
    assert len(all_entries) == 2


def test_list_empty(afile):
    assert list_annotations(path=afile) == []


def test_cmd_add(afile, capsys):
    ns = _ns(afile, expression="* * * * *", note="every minute")
    cmd_add(ns)
    out = capsys.readouterr().out
    assert "every minute" in out


def test_cmd_get_missing_exits(afile):
    ns = _ns(afile, expression="1 2 3 4 5")
    with pytest.raises(SystemExit):
        cmd_get(ns)


def test_cmd_remove(afile, capsys):
    add_note("0 12 * * *", "noon", path=afile)
    ns = _ns(afile, expression="0 12 * * *", note="noon")
    cmd_remove(ns)
    out = capsys.readouterr().out
    assert "0 12 * * *" in out


def test_cmd_list_empty(afile, capsys):
    ns = _ns(afile)
    cmd_list(ns)
    out = capsys.readouterr().out
    assert "No annotations" in out
