"""Common cron expression presets and their human-readable labels."""
from typing import Optional

PRESETS: dict[str, tuple[str, str]] = {
    "@yearly": ("0 0 1 1 *", "Once a year at midnight on January 1st"),
    "@annually": ("0 0 1 1 *", "Once a year at midnight on January 1st"),
    "@monthly": ("0 0 1 * *", "Once a month at midnight on the 1st"),
    "@weekly": ("0 0 * * 0", "Once a week at midnight on Sunday"),
    "@daily": ("0 0 * * *", "Once a day at midnight"),
    "@midnight": ("0 0 * * *", "Once a day at midnight"),
    "@hourly": ("0 * * * *", "Once an hour at the beginning of the hour"),
    "@reboot": ("@reboot", "Run once at startup (not a scheduled expression)"),
}


def resolve_preset(expression: str) -> Optional[tuple[str, str]]:
    """Return (canonical_expression, description) if expression is a preset.

    Returns None if the expression is not a known preset.
    """
    key = expression.strip().lower()
    return PRESETS.get(key)


def is_preset(expression: str) -> bool:
    """Return True if the expression matches a known preset alias."""
    return expression.strip().lower() in PRESETS


def list_presets() -> list[dict]:
    """Return a list of all presets as dicts with alias, expression, description."""
    seen = set()
    result = []
    for alias, (expr, desc) in PRESETS.items():
        if expr not in seen or alias == "@reboot":
            seen.add(expr)
            result.append({"alias": alias, "expression": expr, "description": desc})
    return result
