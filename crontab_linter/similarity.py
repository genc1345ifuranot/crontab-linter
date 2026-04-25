"""Compute similarity scores between two cron expressions."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List

from .parser import CronExpression, parse
from .validator import validate


@dataclass
class SimilarityResult:
    expr_a: str
    expr_b: str
    score: float          # 0.0 (completely different) – 1.0 (identical)
    field_scores: List[float] = field(default_factory=list)
    valid_a: bool = True
    valid_b: bool = True
    errors: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "expr_a": self.expr_a,
            "expr_b": self.expr_b,
            "score": round(self.score, 4),
            "field_scores": [round(s, 4) for s in self.field_scores],
            "valid_a": self.valid_a,
            "valid_b": self.valid_b,
            "errors": self.errors,
        }


def _expand_field(value: str, lo: int, hi: int) -> set:
    """Return the set of integer values a cron field resolves to."""
    full = set(range(lo, hi + 1))
    if value == "*":
        return full
    result: set = set()
    for part in value.split(","):
        if "/" in part:
            base, step = part.split("/", 1)
            step = int(step)
            start = lo if base == "*" else int(base.split("-")[0])
            end = hi if base == "*" else (int(base.split("-")[1]) if "-" in base else hi)
            result.update(range(start, end + 1, step))
        elif "-" in part:
            a, b = part.split("-", 1)
            result.update(range(int(a), int(b) + 1))
        else:
            result.add(int(part))
    return result


_FIELD_BOUNDS = [
    (0, 59),   # minute
    (0, 23),   # hour
    (1, 31),   # day-of-month
    (1, 12),   # month
    (0, 6),    # day-of-week
]


def _jaccard(a: set, b: set) -> float:
    if not a and not b:
        return 1.0
    union = a | b
    if not union:
        return 1.0
    return len(a & b) / len(union)


def compute_similarity(expr_a: str, expr_b: str) -> SimilarityResult:
    errors: list = []
    valid_a, valid_b = True, True

    try:
        pa = parse(expr_a)
        va = validate(pa)
        if not va.valid:
            valid_a = False
            errors.extend(va.errors)
    except Exception as exc:
        valid_a = False
        errors.append(f"expr_a: {exc}")
        pa = None

    try:
        pb = parse(expr_b)
        vb = validate(pb)
        if not vb.valid:
            valid_b = False
            errors.extend(vb.errors)
    except Exception as exc:
        valid_b = False
        errors.append(f"expr_b: {exc}")
        pb = None

    if pa is None or pb is None:
        return SimilarityResult(expr_a, expr_b, 0.0, [], valid_a, valid_b, errors)

    fields_a = [pa.minute, pa.hour, pa.day_of_month, pa.month, pa.day_of_week]
    fields_b = [pb.minute, pb.hour, pb.day_of_month, pb.month, pb.day_of_week]

    scores = [
        _jaccard(
            _expand_field(fa, lo, hi),
            _expand_field(fb, lo, hi),
        )
        for fa, fb, (lo, hi) in zip(fields_a, fields_b, _FIELD_BOUNDS)
    ]

    overall = sum(scores) / len(scores)
    return SimilarityResult(expr_a, expr_b, overall, scores, valid_a, valid_b, errors)
