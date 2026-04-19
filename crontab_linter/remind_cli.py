"""CLI commands for reminders."""
from __future__ import annotations
import argparse
import sys
from crontab_linter.remind import add_reminder, get_reminder, remove_reminder, list_reminders
from crontab_linter.remind_formatter import format_remind, format_remind_list


def cmd_add(ns: argparse.Namespace) -> None:
    tags = [t.strip() for t in ns.tags.split(",") if t.strip()] if ns.tags else []
    entry = add_reminder(ns.expression, ns.message, tags)
    print(format_remind(entry, ns.format))


def cmd_get(ns: argparse.Namespace) -> None:
    entry = get_reminder(ns.expression)
    if entry is None:
        print(f"No reminder for: {ns.expression}", file=sys.stderr)
        sys.exit(1)
    print(format_remind(entry, ns.format))


def cmd_remove(ns: argparse.Namespace) -> None:
    removed = remove_reminder(ns.expression)
    if not removed:
        print(f"No reminder found for: {ns.expression}", file=sys.stderr)
        sys.exit(1)
    print("Reminder removed.")


def cmd_list(ns: argparse.Namespace) -> None:
    entries = list_reminders()
    print(format_remind_list(entries, ns.format))


def build_remind_parser(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser("remind", help="Manage reminders for cron expressions")
    s = p.add_subparsers(dest="remind_cmd", required=True)

    pa = s.add_parser("add"); pa.add_argument("expression"); pa.add_argument("message")
    pa.add_argument("--tags", default=""); pa.add_argument("--format", default="plain"); pa.set_defaults(func=cmd_add)

    pg = s.add_parser("get"); pg.add_argument("expression")
    pg.add_argument("--format", default="plain"); pg.set_defaults(func=cmd_get)

    pr = s.add_parser("remove"); pr.add_argument("expression"); pr.set_defaults(func=cmd_remove)

    pl = s.add_parser("list"); pl.add_argument("--format", default="plain"); pl.set_defaults(func=cmd_list)
