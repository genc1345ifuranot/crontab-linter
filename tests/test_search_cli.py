"""Tests for crontab_linter.search_cli."""
from __future__ import annotations

import argparse
import json
import pytest

from crontab_linter.alias import _save_aliases, AliasEntry
from crontab_linter.snapshot import _save_snapshots, SnapshotEntry
from crontab_linter.tags import _save_tags, TagEntry
from crontab_linter.search_cli import cmd_search, build_search_parser


@pytest.fixture()
def populated(tmp_path, monkeypatch):
    """Patch storage paths and populate with sample data."""
    af = str(tmp_path / "aliases.json")
    tf = str(tmp_path / "tags.json")
    sf = str(tmp_path / "snaps.json")

    _save_aliases([AliasEntry(name="nightjob", expression="0 2 * * *")], alias_file=af)
    _save_tags([TagEntry(expression="0 2 * * *", tags=["nightly"], note="2am run")], tag_file=tf)
    _save_snapshots([SnapshotEntry(name="snap1", expression="0 2 * * *", note="snap")], snapshot_file=sf)

    # Monkeypatch default file paths used by storage loaders
    import crontab_linter.alias as am
    import crontab_linter.tags as tm
    import crontab_linter.snapshot as sm
    monkeypatch.setattr(am, "_DEFAULT_FILE", af)
    monkeypatch.setattr(tm, "_DEFAULT_FILE", tf)
    monkeypatch.setattr(sm, "_DEFAULT_FILE", sf)


def _ns(**kw) -> argparse.Namespace:
    defaults = dict(query="nightly", format="plain", no_aliases=False, no_tags=False, no_snapshots=False)
    defaults.update(kw)
    return argparse.Namespace(**defaults)


def test_cmd_search_plain_output(populated, capsys):
    cmd_search(_ns(query="nightly"))
    out = capsys.readouterr().out
    assert "nightly" in out


def test_cmd_search_json_output(populated, capsys):
    cmd_search(_ns(query="2am run", format="json"))
    out = capsys.readouterr().out
    data = json.loads(out)
    assert "tags" in data
    assert data["total"] >= 1


def test_cmd_search_no_results_exits(populated, capsys):
    with pytest.raises(SystemExit) as exc:
        cmd_search(_ns(query="zzznomatch"))
    assert exc.value.code == 1


def test_cmd_search_empty_query_exits(populated, capsys):
    with pytest.raises(SystemExit) as exc:
        cmd_search(_ns(query="   "))
    assert exc.value.code == 1


def test_build_search_parser_registers_subcommand():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()
    build_search_parser(sub)
    args = parser.parse_args(["search", "backup"])
    assert args.query == "backup"
    assert args.format == "plain"
