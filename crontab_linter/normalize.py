"""Normalize crontab expressions to a canonical form."""
from dataclasses import dataclass
from typing import Optional
from .parser import parse, CronExpression
from .presets import is_preset, resolve_preset


@dataclass
class NormalizeResult:
    original: str
    normalized: Optional[str]
    was_preset: bool
    error: Optional[str] = None

    @property
    def ok(self) -> bool:
        return self.error is None

    def to_dict(self) -> dict:
        return {
            "original": self.original,
            "normalized": self.normalized,
            "was_preset": self.was_preset,
            "error": self.error,
        }


def _normalize_field(value: str) -> str:
    """Lowercase aliases, strip leading zeros from numbers."""
    parts = value.split(",")
    out = []
    for part in parts:
        if "/" in part:
            base, step = part.split("/", 1)
            step = str(int(step)) if step.isdigit() else step
            base = _normalize_simple(base)
            out.append(f"{base}/{step}")
        elif "-" in part:
            lo, hi = part.split("-", 1)
            out.append(f"{_normalize_simple(lo)}-{_normalize_simple(hi)}")
        else:
            out.append(_normalize_simple(part))
    return ",".join(out)


def _normalize_simple(token: str) -> str:
    if token == "*":
        return "*"
    if token.lstrip("-").isdigit():
        return str(int(token))
    return token.upper()


def normalize(expression: str) -> NormalizeResult:
    """Return a canonical representation of a cron expression."""
    original = expression.strip()

    was_preset = is_preset(original)
    if was_preset:
        resolved = resolve_preset(original)
        if resolved is None:
            return NormalizeResult(original, None, True, "Unknown preset")
        expression = resolved

    try:
        expr: CronExpression = parse(expression)
    except Exception as exc:  # noqa: BLE001
        return NormalizeResult(original, None, was_preset, str(exc))

    fields = [
        _normalize_field(expr.minute),
        _normalize_field(expr.hour),
        _normalize_field(expr.day_of_month),
        _normalize_field(expr.month),
        _normalize_field(expr.day_of_week),
    ]
    normalized = " ".join(fields)
    return NormalizeResult(original, normalized, was_preset)
