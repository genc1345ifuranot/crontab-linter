"""CLI command for renaming aliases and templates."""
from __future__ import annotations
import argparse
import json
import sys

from crontab_linter.rename import rename, Kind


def cmd_rename(ns: argparse.Namespace) -> None:
    kind: Kind = ns.kind
    result = rename(kind, ns.old_name, ns.new_name)
    if ns.format == "json":
        print(json.dumps(result.to_dict(), indent=2))
    else:
        if result.ok:
            print(f"Renamed {kind} '{ns.old_name}' -> '{ns.new_name}'")
        else:
            print(f"Error: {result.error}", file=sys.stderr)
    if not result.ok:
        sys.exit(1)


def build_rename_parser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser("rename", help="Rename an alias or template")
    p.add_argument("kind", choices=["alias", "template"], help="Type of entry to rename")
    p.add_argument("old_name", help="Current name")
    p.add_argument("new_name", help="New name")
    p.add_argument("--format", choices=["plain", "json"], default="plain")
    p.set_defaults(func=cmd_rename)
