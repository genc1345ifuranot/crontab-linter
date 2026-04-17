"""Tests for crontab_linter.watch and watch_cli."""
from __future__ import annotations

import argparse
import textwrap
from pathlib import Path

import pytest

from crontab_linter.watch import WatchEvent, watch
from crontab_linter.watch_cli import cmd_watch, _plain_callback, _json_callback


@pytest.fixture()
def cron_file(tmp_path: Path) -> Path:
    p = tmp_path / "crontab"
    p.write_text("* * * * * echo hello\n")
    return p


def test_watch_detects_change(cron_file: Path) -> None:
    events: list[WatchEvent] = []

    def cb(ev: WatchEvent) -> None:
        events.append(ev)

    # Run one iteration — first hash differs from empty string → triggers
    watch(str(cron_file), callback=cb, interval=0, max_iterations=1)
    assert len(events) == 1
    assert events[0].changed is True
    assert events[0].result is not None


def test_watch_no_duplicate_event(cron_file: Path) -> None:
    events: list[WatchEvent] = []

    def cb(ev: WatchEvent) -> None:
        events.append(ev)

    # Two iterations without modifying file: second should not fire
    watch(str(cron_file), callback=cb, interval=0, max_iterations=2)
    assert len(events) == 1


def test_watch_event_result_valid(cron_file: Path) -> None:
    events: list[WatchEvent] = []
    watch(str(cron_file), callback=lambda e: events.append(e), interval=0, max_iterations=1)
    result = events[0].result
    assert result is not None
    assert result.total == 1


def test_watch_event_to_dict(cron_file: Path) -> None:
    events: list[WatchEvent] = []
    watch(str(cron_file), callback=lambda e: events.append(e), interval=0, max_iterations=1)
    d = events[0].to_dict()
    assert d["changed"] is True
    assert isinstance(d["result"], list)


def test_watch_error_event(tmp_path: Path) -> None:
    missing = str(tmp_path / "no_such_file.cron")
    events: list[WatchEvent] = []
    # File doesn't exist → hash is empty → no event fired
    watch(missing, callback=lambda e: events.append(e), interval=0, max_iterations=1)
    assert len(events) == 0


def _ns(file: str, fmt: str = "plain", interval: float = 0.001) -> argparse.Namespace:
    ns = argparse.Namespace(file=file, format=fmt, interval=interval)
    return ns


def test_cmd_watch_plain(cron_file: Path, capsys) -> None:
    ns = _ns(str(cron_file), fmt="plain", interval=0)
    # Patch watch to run only 1 iteration
    import crontab_linter.watch_cli as wc
    original = wc.watch
    calls = []

    def fake_watch(path, callback, interval):
        from crontab_linter.watch import _lint_file
        from pathlib import Path as P
        result = _lint_file(P(path))
        from crontab_linter.watch import WatchEvent
        callback(WatchEvent(path=path, changed=True, result=result))
        calls.append(1)

    wc.watch = fake_watch
    try:
        cmd_watch(ns)
    except SystemExit:
        pass
    finally:
        wc.watch = original

    out = capsys.readouterr().out
    assert "changed" in out


def test_cmd_watch_json(cron_file: Path, capsys) -> None:
    import crontab_linter.watch_cli as wc
    original = wc.watch

    def fake_watch(path, callback, interval):
        from crontab_linter.watch import _lint_file, WatchEvent
        from pathlib import Path as P
        callback(WatchEvent(path=path, changed=True, result=_lint_file(P(path))))

    wc.watch = fake_watch
    try:
        cmd_watch(_ns(str(cron_file), fmt="json"))
    finally:
        wc.watch = original

    import json
    out = capsys.readouterr().out.strip()
    data = json.loads(out)
    assert data["changed"] is True
