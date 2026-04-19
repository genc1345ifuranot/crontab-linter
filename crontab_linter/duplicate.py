from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class DuplicateGroup:
    expression: str
    sources: List[str] = field(default_factory=list)

    def count(self) -> int:
        return len(self.sources)

    def to_dict(self) -> dict:
        return {
            "expression": self.expression,
            "sources": self.sources,
            "count": self.count(),
        }


@dataclass
class DuplicateResult:
    groups: List[DuplicateGroup] = field(default_factory=list)

    def has_duplicates(self) -> bool:
        return len(self.groups) > 0

    def total_duplicates(self) -> int:
        return sum(g.count() - 1 for g in self.groups)

    def to_dict(self) -> dict:
        return {
            "has_duplicates": self.has_duplicates(),
            "total_duplicates": self.total_duplicates(),
            "groups": [g.to_dict() for g in self.groups],
        }


def find_duplicates(entries: Dict[str, str]) -> DuplicateResult:
    """Find duplicate cron expressions across named entries.

    Args:
        entries: mapping of name -> cron expression

    Returns:
        DuplicateResult with grouped duplicates.
    """
    seen: Dict[str, List[str]] = {}
    for name, expr in entries.items():
        normalized = expr.strip()
        seen.setdefault(normalized, []).append(name)

    groups = [
        DuplicateGroup(expression=expr, sources=names)
        for expr, names in seen.items()
        if len(names) > 1
    ]
    return DuplicateResult(groups=groups)
