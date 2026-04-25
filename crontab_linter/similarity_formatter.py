"""Format SimilarityResult for display."""
from __future__ import annotations
import json
from .similarity import SimilarityResult

_FIELD_NAMES = ["minute", "hour", "day-of-month", "month", "day-of-week"]


def format_similarity_plain(result: SimilarityResult) -> str:
    lines = [
        f"Similarity: {result.score:.1%}",
        f"  A: {result.expr_a}",
        f"  B: {result.expr_b}",
        "",
        "Field breakdown:",
    ]
    for name, score in zip(_FIELD_NAMES, result.field_scores):
        bar_len = int(score * 20)
        bar = "#" * bar_len + "-" * (20 - bar_len)
        lines.append(f"  {name:<14} [{bar}] {score:.1%}")

    if result.errors:
        lines.append("")
        lines.append("Errors:")
        for err in result.errors:
            lines.append(f"  - {err}")

    return "\n".join(lines)


def format_similarity_json(result: SimilarityResult) -> str:
    return json.dumps(result.to_dict(), indent=2)


def format_similarity(result: SimilarityResult, fmt: str = "plain") -> str:
    if fmt == "json":
        return format_similarity_json(result)
    return format_similarity_plain(result)
