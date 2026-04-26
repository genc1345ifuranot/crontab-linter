"""Formatters for CompressResult."""
import json
from .compress import CompressResult


def format_compress_plain(result: CompressResult) -> str:
    lines = []
    if not result.ok:
        lines.append(f"Error: {result.error}")
        return "\n".join(lines)

    lines.append(f"Original:   {result.original}")
    lines.append(f"Compressed: {result.compressed}")

    if result.has_changes:
        lines.append("")
        lines.append("Changes:")
        for change in result.changes:
            lines.append(f"  [{change.name}] {change.original!r} -> {change.compressed!r}")
            lines.append(f"    Reason: {change.reason}")
    else:
        lines.append("No compression possible — expression is already minimal.")

    return "\n".join(lines)


def format_compress_json(result: CompressResult) -> str:
    return json.dumps(result.to_dict(), indent=2)


def format_compress(result: CompressResult, fmt: str = "plain") -> str:
    if fmt == "json":
        return format_compress_json(result)
    return format_compress_plain(result)
