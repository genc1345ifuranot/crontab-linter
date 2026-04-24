"""CLI sub-command: overlap — detect scheduling overlaps."""
from __future__ import annotations

import argparse
import sys
import datetime

from .overlap import find_overlaps
from .overlap_formatter import format_overlap


def cmd_overlap(args: argparse.Namespace) -> None:
    expressions = args.expressions
    if not expressions or len(expressions) < 2:
        print("ERROR: Provide at least two cron expressions.", file=sys.stderr)
        sys.exit(1)

    start: datetime.datetime | None = None
    if args.start:
        try:
            start = datetime.datetime.fromisoformat(args.start)
        except ValueError:
            print(f"ERROR: Invalid --start datetime: {args.start!r}", file=sys.stderr)
            sys.exit(1)

    result = find_overlaps(
        expressions,
        start=start,
        minutes=args.minutes,
    )

    print(format_overlap(result, fmt=args.format))

    if result.errors and not result.has_overlaps:
        sys.exit(2)


def build_overlap_parser(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser(
        "overlap",
        help="Detect scheduling overlaps between cron expressions",
    )
    p.add_argument(
        "expressions",
        nargs="+",
        metavar="EXPR",
        help="Two or more cron expressions to compare",
    )
    p.add_argument(
        "--start",
        default=None,
        metavar="ISO_DATETIME",
        help="Start datetime for overlap scan (ISO format, default: now)",
    )
    p.add_argument(
        "--minutes",
        type=int,
        default=1440,
        metavar="N",
        help="Number of minutes to scan (default: 1440 = 24 h)",
    )
    p.add_argument(
        "--format",
        choices=["plain", "json"],
        default="plain",
        help="Output format (default: plain)",
    )
    p.set_defaults(func=cmd_overlap)
