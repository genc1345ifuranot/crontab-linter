"""Formatters for template output (plain text and JSON)."""

from __future__ import annotations

import json
from typing import List

from .template import TemplateEntry


def format_template_plain(entry: TemplateEntry) -> str:
    lines = [
        f"Name       : {entry.name}",
        f"Expression : {entry.expression}",
    ]
    if entry.description:
        lines.append(f"Description: {entry.description}")
    tags_str = ", ".join(entry.tags) if entry.tags else "(none)"
    lines.append(f"Tags       : {tags_str}")
    return "\n".join(lines)


def format_template_json(entry: TemplateEntry) -> str:
    return json.dumps(entry.to_dict(), indent=2)


def format_template_list_plain(entries: List[TemplateEntry]) -> str:
    if not entries:
        return "No templates saved."
    blocks = [format_template_plain(e) for e in entries]
    return "\n\n".join(blocks)


def format_template_list_json(entries: List[TemplateEntry]) -> str:
    return json.dumps([e.to_dict() for e in entries], indent=2)


def format_template(entry: TemplateEntry, fmt: str = "plain") -> str:
    """Format a single template entry.

    Args:
        entry: The template entry to format.
        fmt: Output format — 'plain' or 'json'.

    Returns:
        Formatted string.
    """
    if fmt == "json":
        return format_template_json(entry)
    return format_template_plain(entry)


def format_template_list(entries: List[TemplateEntry], fmt: str = "plain") -> str:
    """Format a list of template entries.

    Args:
        entries: List of template entries.
        fmt: Output format — 'plain' or 'json'.

    Returns:
        Formatted string.
    """
    if fmt == "json":
        return format_template_list_json(entries)
    return format_template_list_plain(entries)
