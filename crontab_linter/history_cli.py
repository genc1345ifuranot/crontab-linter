"""CLI sub-commands for interacting with lint history."""

from __future__ import annotations

import argparse
import json
import sys
from typing import List

from .history import HistoryEntry, clear_history, get_history


def _print_entry(entry: HistoryEntry, index: int) -> None:
    status = "\u2713 valid" if entry.valid else "\u2717 invalid"
    tz_label = f" [{entry.timezone}]" if entry.timezone else ""
    print(f"[{index}] {entry.timestamp}  {status}")
    print(f"     expr : {entry.expression}{tz_label}")
    if entry.errors:
        for e in entry.errors:
            print(f"     error: {e}")
    if entry.warnings:
        for w in entry.warnings:
            print(f"     warn : {w}")
    print(f"     info : {entry.explanation}")


def cmd_list(args: argparse.Namespace) -> int:
    entries = get_history()
    if not entries:
        print("No history found.")
        return 0
    limit: int = args.limit
    shown = entries[-limit:] if limit else entries
    for i, entry in enumerate(shown, start=1):
        _print_entry(entry, i)
        print()
    return 0


def cmd_clear(args: argparse.Namespace) -> int:  # noqa: ARG001
    removed = clear_history()
    print(f"Cleared {removed} history entries.")
    return 0


def cmd_export(args: argparse.Namespace) -> int:
    entries = get_history()
    data = [e.to_dict() for e in entries]
    output = json.dumps(data, indent=2)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(output)
        print(f"Exported {len(entries)} entries to {args.output}")
    else:
        print(output)
    return 0


def build_history_parser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    hist = subparsers.add_parser("history", help="Manage lint history")
    hist_sub = hist.add_subparsers(dest="history_cmd")

    ls = hist_sub.add_parser("list", help="Show recent history")
    ls.add_argument("--limit", type=int, default=20, help="Max entries to show")
    ls.set_defaults(func=cmd_list)

    cl = hist_sub.add_parser("clear", help="Delete all history")
    cl.set_defaults(func=cmd_clear)

    ex = hist_sub.add_parser("export", help="Export history as JSON")
    ex.add_argument("--output", "-o", default="", help="File path (default: stdout)")
    ex.set_defaults(func=cmd_export)
