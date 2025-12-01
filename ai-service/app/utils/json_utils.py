"""JSON utilities."""
import json
from datetime import datetime
from typing import Any


class DateTimeEncoder(json.JSONEncoder):
    """JSON encoder that handles datetime objects."""

    def default(self, obj: Any) -> Any:
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


def to_json(data: Any, pretty: bool = False) -> str:
    """Convert data to JSON string."""
    indent = 2 if pretty else None
    return json.dumps(data, cls=DateTimeEncoder, indent=indent, ensure_ascii=False)


def from_json(json_str: str) -> Any:
    """Parse JSON string to data."""
    return json.loads(json_str)


def safe_parse_json(json_str: str, default: Any = None) -> Any:
    """Safely parse JSON string, returning default on error."""
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return default
