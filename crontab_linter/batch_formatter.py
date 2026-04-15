"""Formatters for BatchResult output (plain text and JSON)."""
from __future__ import annotations

import json
from typing import Literal

from .batch import BatchResult, BatchEntry


def _entry_plain(entry: BatchEntry) -> str:
    lines = []
    header = f"Line {entry.line_number}: {entry.expression or entry.raw}"
    if entry.comment:
        header += f"  # {entry.comment}"
    lines.append(header)

    if entry.parse_error:
        lines.append(f"  [ERROR] Parse error: {entry.parse_error}")
        return "\n".join(lines)

    if entry.validation and not entry.validation.valid:
        for err in entry.validation.errors:
            lines.append(f"  [INVALID] {err}")
    else:
        lines.append(f"  [OK] {entry.explanation}")

    if entry.lint and entry.lint.has_warnings():
        for w in entry.lint.warnings:
            lines.append(f"  [{w.severity.upper()}] {w.message}")

    return "\n".join(lines)


def format_batch_plain(result: BatchResult) -> str:
    parts = [_entry_plain(e) for e in result.entries]
    summary = (
        f"\nSummary: {result.total} expression(s) checked, "
        f"{result.valid_count} valid, {result.invalid_count} invalid."
    )
    parts.append(summary)
    return "\n".join(parts)


def _entry_dict(entry: BatchEntry) -> dict:
    d: dict = {
        "line_number": entry.line_number,
        "raw": entry.raw,
        "expression": entry.expression,
        "comment": entry.comment,
        "valid": entry.is_valid(),
    }
    if entry.parse_error:
        d["parse_error"] = entry.parse_error
    else:
        d["explanation"] = entry.explanation
        d["errors"] = entry.validation.errors if entry.validation else []
        d["warnings"] = (
            [w.to_dict() for w in entry.lint.warnings]
            if entry.lint and entry.lint.has_warnings()
            else []
        )
    return d


def format_batch_json(result: BatchResult) -> str:
    payload = {
        "summary": {
            "total": result.total,
            "valid": result.valid_count,
            "invalid": result.invalid_count,
        },
        "entries": [_entry_dict(e) for e in result.entries],
    }
    return json.dumps(payload, indent=2)


def format_batch(
    result: BatchResult, fmt: Literal["plain", "json"] = "plain"
) -> str:
    if fmt == "json":
        return format_batch_json(result)
    return format_batch_plain(result)
