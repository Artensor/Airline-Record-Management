"""Time utilities for current-time and week-bound computations.
Key ideas:
    - Accept/return timezone-aware datetimes.
"""

from __future__ import annotations
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from typing import Tuple

def now(tz_name: str) -> datetime:
    """Return the current timezone-aware datetime in the given zone.
    Args:
        tz_name: IANA timezone name, e.g., "America/USA".
    """
    return datetime.now(ZoneInfo(tz_name))

def week_bounds_local(dt_local: datetime) -> Tuple[datetime, datetime]:
    """Compute the local week bounds.
    Args:
        dt_local: A timezone-aware local datetime.

    Returns:
        A tuple (start, end) both timezone-aware in the same zone as dt_local.
    """
    if dt_local.tzinfo is None:
        raise ValueError("dt_local must be timezone-aware")
    # Monday is 0; subtract weekday to get back to Monday.
    start = dt_local - timedelta(days=dt_local.weekday())
    start = start.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=6, hours=23, minutes=59, seconds=59, microseconds=999999)
    return start, end

def to_utc(dt_local: datetime) -> datetime:
    """Convert a timezone-aware local datetime to UTC.
    Args:
        dt_local: A timezone-aware datetime in any zone.
    Returns:
        A timezone-aware datetime in UTC.
    """
    return dt_local.astimezone(ZoneInfo("UTC"))