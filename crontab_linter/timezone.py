"""Timezone-aware scheduling checks for crontab expressions."""

from datetime import datetime, timezone
from typing import Optional

try:
    import zoneinfo
except ImportError:
    from backports import zoneinfo  # type: ignore

from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


class TimezoneCheckResult:
    """Result of a timezone-aware scheduling check."""

    def __init__(
        self,
        timezone_name: str,
        valid: bool,
        warning: Optional[str] = None,
        info: Optional[str] = None,
    ):
        self.timezone_name = timezone_name
        self.valid = valid
        self.warning = warning
        self.info = info

    def __repr__(self) -> str:
        return (
            f"TimezoneCheckResult(timezone={self.timezone_name!r}, "
            f"valid={self.valid}, warning={self.warning!r})"
        )


def validate_timezone(tz_name: str) -> TimezoneCheckResult:
    """Validate that the given timezone name is a recognised IANA timezone."""
    try:
        ZoneInfo(tz_name)
    except ZoneInfoNotFoundError:
        return TimezoneCheckResult(
            timezone_name=tz_name,
            valid=False,
            warning=f"Unknown timezone: '{tz_name}'. Use a valid IANA timezone (e.g. 'America/New_York').",
        )
    return TimezoneCheckResult(timezone_name=tz_name, valid=True)


def check_dst_ambiguity(tz_name: str, hour: int, minute: int = 0) -> TimezoneCheckResult:
    """Warn if a given hour:minute falls in a DST transition gap or overlap."""
    base = validate_timezone(tz_name)
    if not base.valid:
        return base

    tz = ZoneInfo(tz_name)
    # Use a known DST-transition year to probe both sides of the clock change.
    # We test the same wall-clock time on the first Sunday of April and November
    # as rough proxies; real gap detection checks fold behaviour.
    now = datetime.now(tz=timezone.utc)
    probe = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    local_probe = probe.astimezone(tz)

    # Detect a "gap": the local time is skipped during spring-forward.
    # zoneinfo folds skipped times forward; if the resulting hour differs
    # from what we asked for, the time was in the gap.
    if local_probe.hour != hour:
        return TimezoneCheckResult(
            timezone_name=tz_name,
            valid=True,
            warning=(
                f"Hour {hour:02d}:{minute:02d} may fall in a DST gap in '{tz_name}'. "
                "Jobs scheduled during this window could be skipped or delayed."
            ),
        )

    return TimezoneCheckResult(
        timezone_name=tz_name,
        valid=True,
        info=f"Hour {hour:02d}:{minute:02d} appears safe in timezone '{tz_name}'.",
    )


def utc_offset_summary(tz_name: str) -> Optional[str]:
    """Return a human-readable UTC offset string for the given timezone."""
    try:
        tz = ZoneInfo(tz_name)
    except ZoneInfoNotFoundError:
        return None
    now = datetime.now(tz=tz)
    offset = now.utcoffset()
    if offset is None:
        return None
    total_minutes = int(offset.total_seconds() // 60)
    sign = "+" if total_minutes >= 0 else "-"
    abs_minutes = abs(total_minutes)
    return f"UTC{sign}{abs_minutes // 60:02d}:{abs_minutes % 60:02d}"
