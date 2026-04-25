"""Interpolate variables into cron expressions before parsing."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, Optional

_VAR_RE = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}|\$([A-Za-z_][A-Za-z0-9_]*)")


@dataclass
class InterpolateResult:
    original: str
    interpolated: str
    variables_used: list[str] = field(default_factory=list)
    missing_variables: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return len(self.missing_variables) == 0

    def to_dict(self) -> dict:
        return {
            "original": self.original,
            "interpolated": self.interpolated,
            "variables_used": self.variables_used,
            "missing_variables": self.missing_variables,
            "ok": self.ok,
        }


def interpolate(expression: str, variables: Optional[Dict[str, str]] = None) -> InterpolateResult:
    """Replace $VAR or ${VAR} placeholders in *expression* using *variables*.

    Unknown variables are left as-is and reported in ``missing_variables``.
    """
    if variables is None:
        variables = {}

    used: list[str] = []
    missing: list[str] = []

    def _replace(m: re.Match) -> str:
        name = m.group(1) or m.group(2)
        if name in variables:
            if name not in used:
                used.append(name)
            return str(variables[name])
        if name not in missing:
            missing.append(name)
        return m.group(0)  # leave placeholder unchanged

    result = _VAR_RE.sub(_replace, expression)
    return InterpolateResult(
        original=expression,
        interpolated=result,
        variables_used=used,
        missing_variables=missing,
    )
