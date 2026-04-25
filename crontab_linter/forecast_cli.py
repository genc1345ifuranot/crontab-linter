"""CLI sub-command: forecast — show next N scheduled run times."""
from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone

from .forecast import compute_forecast
from .forecast_formatter import format_forecast
from .parser import parse
from .presets import is_preset, resolve_preset
from .timezone import validate_timezone


def cmd_forecast(args: argparse.Namespace) -> None:
    expression = args.expression
    if is_preset(expression):
        expression = resolve_preset(expression)

    tz_result = validate_timezone(args.timezone)
    if not tz_result.valid:
        print(f"Error: unknown timezone '{args.timezone}'", file=sys.stderr)
        sys.exit(1)

    try:
        expr = parse(expression)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    after: datetime | None = None
    if args.after:
        try:
            after = datetime.fromisoformat(args.after).replace(tzinfo=timezone.utc)
        except ValueError:
            print(f"Error: invalid --after datetime '{args.after}'", file=sys.stderr)
            sys.exit(1)

    result = compute_forecast(
        expr,
        count=args.count,
        tz_name=args.timezone,
        after=after,
    )
    print(format_forecast(result, fmt=args.format))
    if not result.ok:
        sys.exit(1)


def build_forecast_parser(sub: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = sub.add_parser("forecast", help="Show next N scheduled run times")
    p.add_argument("expression", help="Cron expression or preset (e.g. @daily)")
    p.add_argument("--count", type=int, default=5, metavar="N",
                   help="Number of upcoming runs to show (default: 5)")
    p.add_argument("--timezone", default="UTC", metavar="TZ",
                   help="Timezone name (default: UTC)")
    p.add_argument("--after", default=None, metavar="ISO_DATETIME",
                   help="Start datetime in ISO format (default: now)")
    p.add_argument("--format", choices=["plain", "json"], default="plain")
    p.set_defaults(func=cmd_forecast)
