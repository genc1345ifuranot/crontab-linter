"""CLI commands for the tag feature."""

from __future__ import annotations

import argparse
import json
import sys
from typing import List

from crontab_linter.tags import (
    TagEntry,
    get_by_tag,
    list_tags,
    remove_tag,
    tag_expression,
)


def _print_entry(entry: TagEntry) -> None:
    tags_str = ", ".join(entry.tags) if entry.tags else "(none)"
    print(f"  expr : {entry.expression}")
    print(f"  tags : {tags_str}")
    if entry.note:
        print(f"  note : {entry.note}")
    print()


def cmd_tag(args: argparse.Namespace) -> None:
    tags: List[str] = [t.strip() for t in args.tags.split(",") if t.strip()]
    if not tags:
        print("Error: provide at least one tag.", file=sys.stderr)
        sys.exit(1)
    entry = tag_expression(
        expression=args.expression,
        tags=tags,
        note=args.note or "",
        path=args.tags_file,
    )
    print(f"Tagged '{entry.expression}' with: {', '.join(entry.tags)}")


def cmd_list(args: argparse.Namespace) -> None:
    if args.filter_tag:
        entries = get_by_tag(args.filter_tag, path=args.tags_file)
        if not entries:
            print(f"No expressions tagged '{args.filter_tag}'.")
            return
    else:
        entries = list_tags(path=args.tags_file)
        if not entries:
            print("No tagged expressions found.")
            return
    if getattr(args, "json", False):
        print(json.dumps([e.to_dict() for e in entries], indent=2))
    else:
        for entry in entries:
            _print_entry(entry)


def cmd_remove_tag(args: argparse.Namespace) -> None:
    result = remove_tag(args.expression, args.tag, path=args.tags_file)
    if result is None:
        print(f"Expression not found: {args.expression}", file=sys.stderr)
        sys.exit(1)
    remaining = ", ".join(result.tags) if result.tags else "(none)"
    print(f"Removed tag '{args.tag}'. Remaining tags: {remaining}")


def build_tags_parser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--tags-file", default=None, help="Custom tags storage file")

    p_tag = subparsers.add_parser("tag", parents=[common], help="Tag a cron expression")
    p_tag.add_argument("expression", help="Cron expression to tag")
    p_tag.add_argument("tags", help="Comma-separated list of tags")
    p_tag.add_argument("--note", default="", help="Optional note")
    p_tag.set_defaults(func=cmd_tag)

    p_list = subparsers.add_parser("tags-list", parents=[common], help="List tagged expressions")
    p_list.add_argument("--filter-tag", default=None, help="Filter by tag")
    p_list.add_argument("--json", action="store_true", help="JSON output")
    p_list.set_defaults(func=cmd_list)

    p_rm = subparsers.add_parser("untag", parents=[common], help="Remove a tag from an expression")
    p_rm.add_argument("expression", help="Cron expression")
    p_rm.add_argument("tag", help="Tag to remove")
    p_rm.set_defaults(func=cmd_remove_tag)
