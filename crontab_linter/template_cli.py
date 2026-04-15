"""CLI commands for managing cron expression templates."""

import argparse
import sys

from .template import save_template, get_template, delete_template, list_templates


def _print_entry(entry) -> None:
    tags_str = ", ".join(entry.tags) if entry.tags else "(none)"
    print(f"  Name       : {entry.name}")
    print(f"  Expression : {entry.expression}")
    if entry.description:
        print(f"  Description: {entry.description}")
    print(f"  Tags       : {tags_str}")
    print()


def cmd_save(args) -> None:
    if not args.name or not args.expression:
        print("Error: --name and --expression are required.", file=sys.stderr)
        sys.exit(1)
    tags = args.tags.split(",") if args.tags else []
    tags = [t.strip() for t in tags if t.strip()]
    entry = save_template(
        name=args.name,
        expression=args.expression,
        description=args.description or "",
        tags=tags,
        path=args.template_file,
    )
    print(f"Template '{entry.name}' saved.")


def cmd_get(args) -> None:
    entry = get_template(args.name, path=args.template_file)
    if entry is None:
        print(f"No template found with name '{args.name}'.", file=sys.stderr)
        sys.exit(1)
    _print_entry(entry)


def cmd_delete(args) -> None:
    removed = delete_template(args.name, path=args.template_file)
    if removed:
        print(f"Template '{args.name}' deleted.")
    else:
        print(f"No template found with name '{args.name}'.", file=sys.stderr)
        sys.exit(1)


def cmd_list(args) -> None:
    entries = list_templates(path=args.template_file)
    if not entries:
        print("No templates saved.")
        return
    for entry in entries:
        _print_entry(entry)


def build_template_parser(subparsers) -> None:
    p = subparsers.add_parser("template", help="Manage cron expression templates")
    p.add_argument("--template-file", default=None, help="Path to templates file")
    sub = p.add_subparsers(dest="template_cmd")

    save_p = sub.add_parser("save", help="Save a template")
    save_p.add_argument("--name", required=True)
    save_p.add_argument("--expression", required=True)
    save_p.add_argument("--description", default="")
    save_p.add_argument("--tags", default="", help="Comma-separated tags")
    save_p.set_defaults(func=cmd_save)

    get_p = sub.add_parser("get", help="Get a template by name")
    get_p.add_argument("name")
    get_p.set_defaults(func=cmd_get)

    del_p = sub.add_parser("delete", help="Delete a template by name")
    del_p.add_argument("name")
    del_p.set_defaults(func=cmd_delete)

    list_p = sub.add_parser("list", help="List all templates")
    list_p.set_defaults(func=cmd_list)
