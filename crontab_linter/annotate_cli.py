"""CLI commands for annotation management."""
from __future__ import annotations

import argparse
import sys

from crontab_linter.annotate import add_note, get_notes, list_annotations, remove_note


def _print_entry(entry) -> None:
    print(f"  Expression : {entry.expression}")
    if entry.notes:
        for i, n in enumerate(entry.notes, 1):
            print(f"    [{i}] {n}")
    else:
        print("    (no notes)")


def cmd_add(ns: argparse.Namespace) -> None:
    entry = add_note(ns.expression, ns.note, path=ns.annotate_file)
    print(f"Note added to '{ns.expression}'.")
    _print_entry(entry)


def cmd_get(ns: argparse.Namespace) -> None:
    entry = get_notes(ns.expression, path=ns.annotate_file)
    if entry is None:
        print(f"No annotations found for '{ns.expression}'.")
        sys.exit(1)
    _print_entry(entry)


def cmd_remove(ns: argparse.Namespace) -> None:
    entry = remove_note(ns.expression, ns.note, path=ns.annotate_file)
    print(f"Note removed from '{ns.expression}' (if it existed).")
    _print_entry(entry)


def cmd_list(ns: argparse.Namespace) -> None:
    entries = list_annotations(path=ns.annotate_file)
    if not entries:
        print("No annotations stored.")
        return
    for e in entries:
        _print_entry(e)
        print()


def build_annotate_parser(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser("annotate", help="Manage notes attached to cron expressions")
    p.add_argument("--annotate-file", default=None)
    s = p.add_subparsers(dest="annotate_cmd", required=True)

    pa = s.add_parser("add", help="Add a note")
    pa.add_argument("expression")
    pa.add_argument("note")
    pa.set_defaults(func=cmd_add)

    pg = s.add_parser("get", help="Get notes for an expression")
    pg.add_argument("expression")
    pg.set_defaults(func=cmd_get)

    pr = s.add_parser("remove", help="Remove a note")
    pr.add_argument("expression")
    pr.add_argument("note")
    pr.set_defaults(func=cmd_remove)

    pl = s.add_parser("list", help="List all annotations")
    pl.set_defaults(func=cmd_list)
