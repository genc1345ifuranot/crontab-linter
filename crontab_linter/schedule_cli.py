"""CLI sub-command: ``crontab-linter schedule``."""

from __future__ import annotations

import argparse
import sys

from .parser import CronExpression
from .presets import is_preset, resolve_preset
from .schedule import next_runs
from .schedule_formatter import format_schedule


def cmd_schedule(args: argparse.Namespace) -> int:
    """Handle the *schedule* sub-command.  Returns exit code."""
    raw: str = args.expression

    if is_preset(raw):
        raw = resolve_preset(raw)

    try:
        expr = CronExpression.parse(raw)
    except ValueError as exc:
        print(f"Parse error: {exc}", file=sys.stderr)
        return 1

    result = next_runs(
        expr,
        timezone=args.timezone,
        count=args.count,
    )

    print(format_schedule(result, fmt=args.format))
    return 0 if result.error is None else 1


def build_schedule_parser(subparsers) -> None:  # type: ignore[type-arg]
    """Register the *schedule* sub-command on *subparsers*."""
    p: argparse.ArgumentParser = subparsers.add_parser(
        "schedule",
        help="Show next N run times for a cron expression.",
    )
    p.add_argument("expression", help="Cron expression or preset (e.g. '@daily').")
    p.add_argument(
        "--timezone",
        "-z",
        default="UTC",
        metavar="TZ",
        help="IANA timezone name (default: UTC).",
    )
    p.add_argument(
        "--count",
        "-n",
        type=int,
        default=5,
        metavar="N",
        help="Number of upcoming runs to show (default: 5).",
    )
    p.add_argument(
        "--format",
        "-f",
        choices=["plain", "json"],
        default="plain",
        help="Output format (default: plain).",
    )
    p.set_defaults(func=cmd_schedule)
