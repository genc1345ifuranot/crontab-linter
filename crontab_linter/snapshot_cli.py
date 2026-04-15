"""CLI commands for cron expression snapshots."""
from __future__ import annotations

import argparse
import sys

from crontab_linter.diff import diff_expressions
from crontab_linter.diff_formatter import format_diff
from crontab_linter.parser import parse
from crontab_linter.snapshot import (
    DEFAULT_SNAPSHOT_FILE,
    delete_snapshot,
    get_snapshot,
    list_snapshots,
    save_snapshot,
)


def _print_entry(entry) -> None:
    print(f"  [{entry.name}] {entry.expression}")
    if entry.note:
        print(f"    note: {entry.note}")
    print(f"    saved: {entry.created_at}")


def cmd_save(ns: argparse.Namespace) -> None:
    try:
        parse(ns.expression)
    except ValueError as exc:
        print(f"Error: invalid expression — {exc}", file=sys.stderr)
        sys.exit(1)
    entry = save_snapshot(ns.name, ns.expression, note=ns.note or "",
                          path=ns.snapshot_file)
    print(f"Snapshot '{entry.name}' saved.")


def cmd_get(ns: argparse.Namespace) -> None:
    entry = get_snapshot(ns.name, path=ns.snapshot_file)
    if entry is None:
        print(f"No snapshot named '{ns.name}'.", file=sys.stderr)
        sys.exit(1)
    _print_entry(entry)


def cmd_delete(ns: argparse.Namespace) -> None:
    removed = delete_snapshot(ns.name, path=ns.snapshot_file)
    if not removed:
        print(f"No snapshot named '{ns.name}'.", file=sys.stderr)
        sys.exit(1)
    print(f"Snapshot '{ns.name}' deleted.")


def cmd_list(ns: argparse.Namespace) -> None:
    entries = list_snapshots(path=ns.snapshot_file)
    if not entries:
        print("No snapshots saved.")
        return
    for e in entries:
        _print_entry(e)


def cmd_compare(ns: argparse.Namespace) -> None:
    entry = get_snapshot(ns.name, path=ns.snapshot_file)
    if entry is None:
        print(f"No snapshot named '{ns.name}'.", file=sys.stderr)
        sys.exit(1)
    try:
        old_expr = parse(entry.expression)
        new_expr = parse(ns.expression)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
    result = diff_expressions(old_expr, new_expr)
    fmt = getattr(ns, "format", "plain")
    print(format_diff(result, fmt=fmt))


def build_snapshot_parser(subparsers) -> None:
    p = subparsers.add_parser("snapshot", help="Manage cron expression snapshots")
    p.add_argument("--snapshot-file", default=DEFAULT_SNAPSHOT_FILE)
    sub = p.add_subparsers(dest="snapshot_cmd", required=True)

    ps = sub.add_parser("save", help="Save a snapshot")
    ps.add_argument("name")
    ps.add_argument("expression")
    ps.add_argument("--note", default="")
    ps.set_defaults(func=cmd_save)

    pg = sub.add_parser("get", help="Show a snapshot")
    pg.add_argument("name")
    pg.set_defaults(func=cmd_get)

    pd = sub.add_parser("delete", help="Delete a snapshot")
    pd.add_argument("name")
    pd.set_defaults(func=cmd_delete)

    pl = sub.add_parser("list", help="List all snapshots")
    pl.set_defaults(func=cmd_list)

    pc = sub.add_parser("compare", help="Diff snapshot against a new expression")
    pc.add_argument("name")
    pc.add_argument("expression")
    pc.add_argument("--format", choices=["plain", "json"], default="plain")
    pc.set_defaults(func=cmd_compare)
