"""CLI sub-command: similarity — compare two cron expressions."""
from __future__ import annotations
import argparse
import sys

from .similarity import compute_similarity
from .similarity_formatter import format_similarity


def cmd_similarity(args: argparse.Namespace) -> None:
    result = compute_similarity(args.expr_a, args.expr_b)

    if not result.valid_a or not result.valid_b:
        print(format_similarity(result, fmt=args.format))
        sys.exit(1)

    print(format_similarity(result, fmt=args.format))

    if args.threshold is not None and result.score < args.threshold:
        sys.exit(2)


def build_similarity_parser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser(
        "similarity",
        help="Compute similarity score between two cron expressions",
    )
    p.add_argument("expr_a", help="First cron expression")
    p.add_argument("expr_b", help="Second cron expression")
    p.add_argument(
        "--format",
        choices=["plain", "json"],
        default="plain",
        help="Output format (default: plain)",
    )
    p.add_argument(
        "--threshold",
        type=float,
        default=None,
        metavar="FLOAT",
        help="Exit with code 2 if score is below this value (0.0–1.0)",
    )
    p.set_defaults(func=cmd_similarity)
