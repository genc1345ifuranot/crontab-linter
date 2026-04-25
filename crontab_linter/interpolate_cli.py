"""CLI sub-command: interpolate variables into a cron expression."""
from __future__ import annotations

import argparse
import sys

from .interpolate import interpolate
from .interpolate_formatter import format_interpolate


def cmd_interpolate(args: argparse.Namespace) -> None:
    variables: dict[str, str] = {}
    for pair in args.var or []:
        if "=" not in pair:
            print(f"Invalid variable definition (expected KEY=VALUE): {pair!r}", file=sys.stderr)
            sys.exit(2)
        key, _, value = pair.partition("=")
        variables[key.strip()] = value.strip()

    result = interpolate(args.expression, variables)
    print(format_interpolate(result, fmt=args.format))

    if not result.ok:
        sys.exit(1)


def build_interpolate_parser(subparsers: argparse._SubParsersAction) -> argparse.ArgumentParser:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "interpolate",
        help="Substitute $VAR / ${VAR} placeholders in a cron expression",
    )
    p.add_argument("expression", help="Cron expression possibly containing variable placeholders")
    p.add_argument(
        "--var",
        metavar="KEY=VALUE",
        action="append",
        help="Variable definition; may be repeated",
    )
    p.add_argument(
        "--format",
        choices=["plain", "json"],
        default="plain",
        help="Output format (default: plain)",
    )
    p.set_defaults(func=cmd_interpolate)
    return p
