"""CLI sub-command: coverage."""
from __future__ import annotations

import argparse
import sys

from .coverage import compute_coverage
from .coverage_formatter import format_coverage


def cmd_coverage(args: argparse.Namespace) -> None:
    result = compute_coverage(args.expression)
    print(format_coverage(result, fmt=args.format))
    if not result.ok:
        sys.exit(1)


def build_coverage_parser(sub: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = sub.add_parser(
        "coverage",
        help="Show time-dimension coverage metrics for a cron expression.",
    )
    p.add_argument("expression", help="Cron expression to analyse.")
    p.add_argument(
        "--format",
        choices=["plain", "json"],
        default="plain",
        help="Output format (default: plain).",
    )
    p.set_defaults(func=cmd_coverage)
