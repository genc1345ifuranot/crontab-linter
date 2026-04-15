"""Tests for crontab_linter.search."""
from __future__ import annotations

import json
import pytest

from crontab_linter.alias import _save_aliases, AliasEntry
from crontab_linter.tags import _save_tags, TagEntry
from crontab_linter.snapshot import _save_snapshots, SnapshotEntry
from crontab_linter.search import search


@pytest.fixture()
def data_files(tmp_path):
    alias_file = str(tmp_path / "aliases.json")
    tag_file = str(tmp_path / "tags.json")
    snap_file = str(tmp_path / "snapshots.json")

    _save_aliases(
        [AliasEntry(name="backup", expression="0 2 * * *"),
         AliasEntry(name="deploy", expression="30 6 * * 1")],
        alias_file=alias_file,
    )
    _save_tags(
        [TagEntry(expression="0 2 * * *", tags=["nightly", "backup"], note="runs at 2am"),
         TagEntry(expression="*/5 * * * *", tags=["monitoring"], note=None)],
        tag_file=tag_file,
    )
    _save_snapshots(
        [SnapshotEntry(name="v1", expression="0 0 * * *", note="midnight job"),
         SnapshotEntry(name="v2", expression="0 12 * * *", note=None)],
        snapshot_file=snap_file,
    )
    return alias_file, tag_file, snap_file


def _search(query, data_files, **kw):
    af, tf, sf = data_files
    return search(query, alias_file=af, tag_file=tf, snapshot_file=sf, **kw)


def test_search_alias_by_name(data_files):
    r = _search("backup", data_files)
    assert any(a.name == "backup" for a in r.aliases)


def test_search_alias_by_expression(data_files):
    r = _search("30 6", data_files)
    assert any(a.name == "deploy" for a in r.aliases)


def test_search_tag_by_tag_value(data_files):
    r = _search("nightly", data_files)
    assert any("nightly" in t.tags for t in r.tags)


def test_search_tag_by_note(data_files):
    r = _search("2am", data_files)
    assert len(r.tags) == 1
    assert r.tags[0].note == "runs at 2am"


def test_search_snapshot_by_name(data_files):
    r = _search("v1", data_files)
    assert any(s.name == "v1" for s in r.snapshots)


def test_search_snapshot_by_note(data_files):
    r = _search("midnight", data_files)
    assert any(s.note == "midnight job" for s in r.snapshots)


def test_search_no_results(data_files):
    r = _search("zzznomatch", data_files)
    assert r.is_empty()
    assert r.total == 0


def test_search_skip_aliases(data_files):
    r = _search("backup", data_files, search_aliases=False)
    assert r.aliases == []


def test_search_skip_tags(data_files):
    r = _search("nightly", data_files, search_tags=False)
    assert r.tags == []


def test_search_skip_snapshots(data_files):
    r = _search("midnight", data_files, search_snapshots=False)
    assert r.snapshots == []


def test_search_total_counts(data_files):
    r = _search("0 2 * * *", data_files)
    # matches alias 'backup' and tag '0 2 * * *'
    assert r.total >= 2
