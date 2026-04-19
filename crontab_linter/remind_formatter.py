"""Formatters for reminder entries."""
from __future__ import annotations
import json
from typing import List
from crontab_linter.remind import ReminderEntry


def format_remind_plain(entry: ReminderEntry) -> str:
    lines = [f"Expression : {entry.expression}", f"Message    : {entry.message}"]
    if entry.tags:
        lines.append(f"Tags       : {', '.join(entry.tags)}")
    return "\n".join(lines)


def format_remind_list_plain(entries: List[ReminderEntry]) -> str:
    if not entries:
        return "No reminders stored."
    return "\n\n".join(format_remind_plain(e) for e in entries)


def format_remind_json(entry: ReminderEntry) -> str:
    return json.dumps(entry.to_dict(), indent=2)


def format_remind_list_json(entries: List[ReminderEntry]) -> str:
    return json.dumps([e.to_dict() for e in entries], indent=2)


def format_remind(entry: ReminderEntry, fmt: str = "plain") -> str:
    if fmt == "json":
        return format_remind_json(entry)
    return format_remind_plain(entry)


def format_remind_list(entries: List[ReminderEntry], fmt: str = "plain") -> str:
    if fmt == "json":
        return format_remind_list_json(entries)
    return format_remind_list_plain(entries)
