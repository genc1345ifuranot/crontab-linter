"""CLI command for maturity assessment."""
from __future__ import annotations
import argparse
import sys

from crontab_linter.maturity import assess_maturity
from crontab_linter.maturity_formatter import format_maturity


def cmd_maturity(args: argparse.Namespace) -> None:
    result = assess_maturity(args.expression)
    print(format_maturity(result, fmt=args.format))
    if result.grade in ("D", "F"):
        sys.exit(1)


def build_maturity_parser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser(
        "maturity",
        help="Score a cron expression for production readiness (0-100).",
    )
    p.add_argument("expression", help="Cron expression to assess.")
    p.add_argument(
        "--format",
        choices=["plain", "json"],
        default="plain",
        help="Output format (default: plain).",
    )
    p.set_defaults(func=cmd_maturity)
