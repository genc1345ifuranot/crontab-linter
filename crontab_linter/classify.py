"""Classify a cron expression into a human-readable category with frequency info."""
from dataclasses import dataclass
from typing import Optional
from crontab_linter.parser import parse


@dataclass
class ClassifyResult:
    expression: str
    category: str
    frequency: str
    description: str
    valid: bool
    error: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "expression": self.expression,
            "category": self.category,
            "frequency": self.frequency,
            "description": self.description,
            "valid": self.valid,
            "error": self.error,
        }


def classify(expression: str) -> ClassifyResult:
    try:
        expr = parse(expression)
    except ValueError as exc:
        return ClassifyResult(
            expression=expression,
            category="unknown",
            frequency="unknown",
            description="Invalid expression",
            valid=False,
            error=str(exc),
        )

    m, h, dom, mon, dow = (
        expr.minute, expr.hour, expr.day_of_month, expr.month, expr.day_of_week
    )

    def is_wild(f) -> bool:
        return f.raw == "*"

    # Classify by pattern
    if is_wild(m) and is_wild(h) and is_wild(dom) and is_wild(mon) and is_wild(dow):
        return ClassifyResult(expression, "every-minute", "minutely",
                              "Runs every minute", True)

    if not is_wild(m) and is_wild(h) and is_wild(dom) and is_wild(mon) and is_wild(dow):
        return ClassifyResult(expression, "hourly", "hourly",
                              f"Runs once per hour at minute {m.raw}", True)

    if not is_wild(m) and not is_wild(h) and is_wild(dom) and is_wild(mon) and not is_wild(dow):
        return ClassifyResult(expression, "weekly", "weekly",
                              f"Runs weekly on day-of-week {dow.raw} at {h.raw}:{m.raw}", True)

    if not is_wild(m) and not is_wild(h) and not is_wild(dom) and is_wild(mon) and is_wild(dow):
        return ClassifyResult(expression, "monthly", "monthly",
                              f"Runs monthly on day {dom.raw} at {h.raw}:{m.raw}", True)

    if not is_wild(m) and not is_wild(h) and not is_wild(dom) and not is_wild(mon) and is_wild(dow):
        return ClassifyResult(expression, "yearly", "yearly",
                              f"Runs yearly on {mon.raw}/{dom.raw} at {h.raw}:{m.raw}", True)

    if not is_wild(m) and not is_wild(h) and is_wild(dom) and is_wild(mon) and is_wild(dow):
        return ClassifyResult(expression, "daily", "daily",
                              f"Runs daily at {h.raw}:{m.raw}", True)

    if m.raw.startswith("*/") and is_wild(h) and is_wild(dom) and is_wild(mon) and is_wild(dow):
        step = m.raw[2:]
        return ClassifyResult(expression, "interval", f"every-{step}-minutes",
                              f"Runs every {step} minutes", True)

    return ClassifyResult(expression, "custom", "custom",
                          "Custom schedule with mixed constraints", True)
