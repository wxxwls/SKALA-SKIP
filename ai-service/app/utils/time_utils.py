"""Time and date utilities."""
from datetime import datetime, timezone
from typing import Optional


def utc_now() -> datetime:
    """Get current UTC datetime."""
    return datetime.now(timezone.utc)


def format_datetime(dt: datetime, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format datetime to string."""
    return dt.strftime(fmt)


def parse_datetime(date_str: str, fmt: str = "%Y-%m-%d %H:%M:%S") -> Optional[datetime]:
    """Parse string to datetime."""
    try:
        return datetime.strptime(date_str, fmt)
    except ValueError:
        return None


def to_iso_format(dt: datetime) -> str:
    """Convert datetime to ISO format string."""
    return dt.isoformat()
