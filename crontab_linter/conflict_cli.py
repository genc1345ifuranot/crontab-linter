"""CLI command for detecting conflicts between two cron expressions."""
from __future__ import annotations

import argparse
import sys
import datetime

from .conflict import find_conflicts
from .conflict_formatter import format_conflict


def cmd_conflict(args: argparse.Namespace) -> None:
    start: datetime.datetime | None = None
    if args.start:
        try:
            start = datetime.datetime.fromisoformat(args.start)
        except ValueError:
            print(f"Error: invalid --start datetime '{args.start}'", file=sys.stderr)
            sys.exit(2)

    result = find_conflicts(
        args.expr_a,
        args.expr_b,
        window_hours=args.window,
        start=start,
        max_overlaps=args.max_overlaps,
    )

    print(format_conflict(result, fmt=args.format))

    if not result.valid:
        sys.exit(2)
    if result.has_conflict:
        sys.exit(1)


def build_conflict_parser(sub: argparse._SubParsersAction) -> argparse.ArgumentParser:  # type: ignore[type-arg]
    p = sub.add_parser(
        "conflict",
        help="Detect scheduling conflicts between two cron expressions",
    )
    p.add_argument("expr_a", help="First cron expression")
    p.add_argument("expr_b", help="Second cron expression")
    p.add_argument(
        "--window",
        type=int,
        default=24,
        metavar="HOURS",
        help="Look-ahead window in hours (default: 24)",
    )
    p.add_argument(
        "--start",
        default=None,
        metavar="DATETIME",
        help="ISO-8601 start datetime (default: 2024-01-01T00:00)",
    )
    p.add_argument(
        "--max-overlaps",
        type=int,
        default=10,
        dest="max_overlaps",
        help="Maximum overlaps to report (default: 10)",
    )
    p.add_argument(
        "--format",
        choices=["plain", "json"],
        default="plain",
        help="Output format (default: plain)",
    )
    p.set_defaults(func=cmd_conflict)
    return p
