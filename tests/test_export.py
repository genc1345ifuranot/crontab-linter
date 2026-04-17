"""Tests for crontab_linter.export."""
import json
import pytest

from crontab_linter.alias import _save_aliases, AliasEntry
from crontab_linter.tags import _save_tags, TagEntry
from crontab_linter.snapshot import _save_snapshots, SnapshotEntry
from crontab_linter.export import export_all, format_export, ExportResult


@pytest.fixture()
def data_files(tmp_path):
    alias_file = str(tmp_path / "aliases.json")
    tag_file = str(tmp_path / "tags.json")
    snap_file = str(tmp_path / "snapshots.json")

    _save_aliases([AliasEntry(name="daily", expression="0 0 * * *")], path=alias_file)
    _save_tags([TagEntry(expression="*/5 * * * *", tags=["frequent"])], path=tag_file)
    _save_snapshots([SnapshotEntry(name="v1", expression="0 12 * * 1")], path=snap_file)

    return alias_file, tag_file, snap_file


def test_export_all_returns_result(data_files):
    a, t, s = data_files
    result = export_all(alias_file=a, tag_file=t, snap_file=s)
    assert isinstance(result, ExportResult)


def test_export_total(data_files):
    a, t, s = data_files
    result = export_all(alias_file=a, tag_file=t, snap_file=s)
    assert result.total() == 3


def test_export_aliases(data_files):
    a, t, s = data_files
    result = export_all(alias_file=a, tag_file=t, snap_file=s)
    assert len(result.aliases) == 1
    assert result.aliases[0]["name"] == "daily"


def test_export_tags(data_files):
    a, t, s = data_files
    result = export_all(alias_file=a, tag_file=t, snap_file=s)
    assert len(result.tags) == 1
    assert "frequent" in result.tags[0]["tags"]


def test_export_snapshots(data_files):
    a, t, s = data_files
    result = export_all(alias_file=a, tag_file=t, snap_file=s)
    assert len(result.snapshots) == 1
    assert result.snapshots[0]["name"] == "v1"


def test_format_export_json(data_files):
    a, t, s = data_files
    result = export_all(alias_file=a, tag_file=t, snap_file=s)
    output = format_export(result, fmt="json")
    parsed = json.loads(output)
    assert parsed["total"] == 3
    assert "aliases" in parsed


def test_format_export_plain(data_files):
    a, t, s = data_files
    result = export_all(alias_file=a, tag_file=t, snap_file=s)
    output = format_export(result, fmt="plain")
    assert "daily" in output
    assert "frequent" in output
    assert "v1" in output


def test_format_export_plain_empty(tmp_path):
    result = ExportResult()
    output = format_export(result)
    assert "No data" in output


def test_to_dict_structure(data_files):
    a, t, s = data_files
    result = export_all(alias_file=a, tag_file=t, snap_file=s)
    d = result.to_dict()
    assert set(d.keys()) == {"aliases", "tags", "snapshots", "total"}
