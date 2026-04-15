"""CLI sub-command: search."""
from __future__ import annotations

import argparse
import sys

from crontab_linter.search import search
from crontab_linter.search_formatter import format_search


def cmd_search(args: argparse.Namespace) -> None:
    query = args.query.strip()
    if not query:
        print("Error: search query must not be empty.", file=sys.stderr)
        sys.exit(1)

    result = search(
        query,
        search_aliases=not args.no_aliases,
        search_tags=not args.no_tags,
        search_snapshots=not args.no_snapshots,
    )

    output = format_search(result, query, fmt=args.format)
    print(output)

    if result.is_empty():
        sys.exit(1)


def build_search_parser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser("search", help="Search aliases, tags, and snapshots")
    p.add_argument("query", help="Text to search for")
    p.add_argument(
        "--format",
        choices=["plain", "json"],
        default="plain",
        help="Output format (default: plain)",
    )
    p.add_argument("--no-aliases", action="store_true", help="Skip alias search")
    p.add_argument("--no-tags", action="store_true", help="Skip tag search")
    p.add_argument("--no-snapshots", action="store_true", help="Skip snapshot search")
    p.set_defaults(func=cmd_search)
