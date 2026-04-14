"""CLI entry point for crontab-linter."""

import argparse
import sys

from crontab_linter.parser import parse
from crontab_linter.validator import validate
from crontab_linter.explainer import explain


def _print_result(expression: str, show_explain: bool) -> int:
    result = validate(expression)

    if result.errors:
        print(f"[INVALID] {expression!r}")
        for error in result.errors:
            print(f"  ERROR: {error}")
        return 1

    print(f"[VALID]   {expression!r}")

    if result.warnings:
        for warning in result.warnings:
            print(f"  WARN:  {warning}")

    if show_explain:
        expr = parse(expression)
        if expr:
            print(f"  INFO:  {explain(expr)}")

    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="crontab-linter",
        description="Validate and explain crontab expressions.",
    )
    parser.add_argument(
        "expression",
        nargs="?",
        help="Crontab expression to validate (e.g. '*/5 * * * *').",
    )
    parser.add_argument(
        "--explain", "-e",
        action="store_true",
        help="Print a human-readable explanation of the expression.",
    )
    parser.add_argument(
        "--file", "-f",
        metavar="FILE",
        help="Validate all expressions listed in a file (one per line).",
    )

    args = parser.parse_args(argv)
    exit_code = 0

    if args.file:
        try:
            with open(args.file) as fh:
                lines = [ln.strip() for ln in fh if ln.strip() and not ln.startswith("#")]
        except FileNotFoundError:
            print(f"Error: file '{args.file}' not found.", file=sys.stderr)
            return 2

        for line in lines:
            code = _print_result(line, args.explain)
            if code != 0:
                exit_code = code
        return exit_code

    if args.expression:
        return _print_result(args.expression, args.explain)

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
