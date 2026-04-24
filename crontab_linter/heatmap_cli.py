"""CLI command for the heatmap feature."""
from __future__ import annotations

import argparse
import sys
from typing import List

from crontab_linter.heatmap import compute_heatmap
from crontab_linter.heatmap_formatter import format_heatmap


def cmd_heatmap(args: argparse.Namespace) -> None:
    expression: str = " ".join(args.expression)
    result = compute_heatmap(expression)
    print(format_heatmap(result, fmt=args.format))
    if not result.valid:
        sys.exit(1)


def build_heatmap_parser(
    subparsers: "argparse._SubParsersAction[argparse.ArgumentParser]",
) -> None:
    p = subparsers.add_parser(
        "heatmap",
        help="Show execution frequency heatmap for a cron expression",
    )
    p.add_argument(
        "expression",
        nargs="+",
        help='Cron expression, e.g. "*/15 9-17 * * 1-5"',
    )
    p.add_argument(
        "--format",
        choices=["plain", "json"],
        default="plain",
        help="Output format (default: plain)",
    )
    p.set_defaults(func=cmd_heatmap)
