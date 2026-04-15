"""CLI sub-commands for managing cron expression aliases."""
from __future__ import annotations

import argparse
import json
import sys

from crontab_linter.alias import (
    AliasEntry,
    delete_alias,
    get_alias,
    list_aliases,
    save_alias,
)


def _print_entry(entry: AliasEntry) -> None:
    desc = f"  # {entry.description}" if entry.description else ""
    print(f"{entry.name:<20} {entry.expression}{desc}")


def cmd_save(args: argparse.Namespace) -> None:
    entry = save_alias(
        name=args.name,
        expression=args.expression,
        description=args.description or "",
        path=args.alias_file,
    )
    print(f"Alias '{entry.name}' saved → {entry.expression}")


def cmd_get(args: argparse.Namespace) -> None:
    entry = get_alias(args.name, path=args.alias_file)
    if entry is None:
        print(f"Alias '{args.name}' not found.", file=sys.stderr)
        sys.exit(1)
    _print_entry(entry)


def cmd_delete(args: argparse.Namespace) -> None:
    removed = delete_alias(args.name, path=args.alias_file)
    if removed:
        print(f"Alias '{args.name}' deleted.")
    else:
        print(f"Alias '{args.name}' not found.", file=sys.stderr)
        sys.exit(1)


def cmd_list(args: argparse.Namespace) -> None:
    entries = list_aliases(path=args.alias_file)
    if not entries:
        print("No aliases saved.")
        return
    if getattr(args, "json", False):
        print(json.dumps([e.to_dict() for e in entries], indent=2))
    else:
        for entry in entries:
            _print_entry(entry)


def build_alias_parser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    alias_parser = subparsers.add_parser("alias", help="Manage cron expression aliases")
    alias_parser.add_argument("--alias-file", default=None, help="Path to alias storage file")
    alias_sub = alias_parser.add_subparsers(dest="alias_cmd", required=True)

    # save
    p_save = alias_sub.add_parser("save", help="Save a named alias")
    p_save.add_argument("name", help="Alias name")
    p_save.add_argument("expression", help="Cron expression")
    p_save.add_argument("--description", "-d", default="", help="Optional description")
    p_save.set_defaults(func=cmd_save)

    # get
    p_get = alias_sub.add_parser("get", help="Show a single alias")
    p_get.add_argument("name", help="Alias name")
    p_get.set_defaults(func=cmd_get)

    # delete
    p_del = alias_sub.add_parser("delete", help="Delete an alias")
    p_del.add_argument("name", help="Alias name")
    p_del.set_defaults(func=cmd_delete)

    # list
    p_list = alias_sub.add_parser("list", help="List all aliases")
    p_list.add_argument("--json", action="store_true", help="Output as JSON")
    p_list.set_defaults(func=cmd_list)
