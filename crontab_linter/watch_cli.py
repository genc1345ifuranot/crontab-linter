"""CLI sub-command: watch a crontab file for changes."""
from __future__ import annotations

import argparse
import json
import sys

from crontab_linter.watch import WatchEvent, watch


def _plain_callback(event: WatchEvent) -> None:
    print(f"[changed] {event.path}")
    if event.error:
        print(f"  ERROR: {event.error}", file=sys.stderr)
        return
    if event.result is None:
        return
    valid = sum(1 for e in event.result.entries if e.is_valid)
    total = event.result.total
    print(f"  {valid}/{total} expressions valid")
    for entry in event.result.entries:
        if not entry.is_valid:
            print(f"  INVALID: {entry.expression!r} — {', '.join(entry.errors)}")


def _json_callback(event: WatchEvent) -> None:
    print(json.dumps(event.to_dict()))
    sys.stdout.flush()


def cmd_watch(ns: argparse.Namespace) -> None:
    fmt = getattr(ns, "format", "plain")
    callback = _json_callback if fmt == "json" else _plain_callback
    interval = getattr(ns, "interval", 1.0)

    print(f"Watching {ns.file} (interval={interval}s) — Ctrl-C to stop", file=sys.stderr)
    try:
        watch(ns.file, callback=callback, interval=interval)
    except KeyboardInterrupt:
        print("Stopped.", file=sys.stderr)


def build_watch_parser(sub: argparse._SubParsersAction) -> None:  # noqa: SLF001
    p = sub.add_parser("watch", help="Watch a crontab file and re-lint on change")
    p.add_argument("file", help="Path to crontab file")
    p.add_argument("--interval", type=float, default=1.0, help="Poll interval in seconds")
    p.add_argument("--format", choices=["plain", "json"], default="plain")
    p.set_defaults(func=cmd_watch)
