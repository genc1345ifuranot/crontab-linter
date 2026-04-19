"""CLI commands for pinning cron expressions."""
from __future__ import annotations
import argparse
import sys
from crontab_linter.pin import pin, unpin, list_pins, get_pin, DEFAULT_PIN_FILE


def _print_entry(e) -> None:
    label = f"  label : {e.label}" if e.label else ""
    tags = f"  tags  : {', '.join(e.tags)}" if e.tags else ""
    print(f"  expr  : {e.expression}")
    if label:
        print(label)
    if tags:
        print(tags)


def cmd_pin(ns: argparse.Namespace) -> None:
    tags = ns.tags.split(",") if getattr(ns, "tags", None) else []
    entry = pin(ns.expression, label=getattr(ns, "label", None), tags=tags,
                path=getattr(ns, "pin_file", DEFAULT_PIN_FILE))
    print("Pinned:")
    _print_entry(entry)


def cmd_unpin(ns: argparse.Namespace) -> None:
    removed = unpin(ns.expression, path=getattr(ns, "pin_file", DEFAULT_PIN_FILE))
    if removed:
        print(f"Unpinned: {ns.expression}")
    else:
        print(f"Not found: {ns.expression}", file=sys.stderr)
        sys.exit(1)


def cmd_list(ns: argparse.Namespace) -> None:
    entries = list_pins(path=getattr(ns, "pin_file", DEFAULT_PIN_FILE))
    if not entries:
        print("No pinned expressions.")
        return
    for e in entries:
        _print_entry(e)
        print()


def cmd_get(ns: argparse.Namespace) -> None:
    entry = get_pin(ns.expression, path=getattr(ns, "pin_file", DEFAULT_PIN_FILE))
    if entry is None:
        print(f"Not found: {ns.expression}", file=sys.stderr)
        sys.exit(1)
    _print_entry(entry)


def build_pin_parser(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser("pin", help="Pin a cron expression")
    p.add_argument("expression")
    p.add_argument("--label", default=None)
    p.add_argument("--tags", default=None, help="Comma-separated tags")
    p.set_defaults(func=cmd_pin)

    u = sub.add_parser("unpin", help="Unpin a cron expression")
    u.add_argument("expression")
    u.set_defaults(func=cmd_unpin)

    ls = sub.add_parser("pins", help="List pinned expressions")
    ls.set_defaults(func=cmd_list)

    g = sub.add_parser("pin-get", help="Get a pinned expression")
    g.add_argument("expression")
    g.set_defaults(func=cmd_get)
