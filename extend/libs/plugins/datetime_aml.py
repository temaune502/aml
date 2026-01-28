"""
Datetime модуль для AML: поточний час, форматування та timestamp.
"""

import datetime as dt_module
from datetime import timezone

def now_iso():
    """Поточний час у ISO 8601 (UTC)."""
    return dt_module.datetime.now(timezone.utc).isoformat()

def timestamp():
    """Поточний timestamp у секундах (float)."""
    return dt_module.datetime.now(timezone.utc).timestamp()

def format_now(fmt="%Y-%m-%d %H:%M:%S"):
    """Відформатований поточний час у локальній зоні."""
    return dt_module.datetime.now().strftime(fmt)

def format_timestamp(ts, fmt="%Y-%m-%d %H:%M:%S"):
    """Форматувати переданий timestamp (секунди) у рядок."""
    dt = dt_module.datetime.fromtimestamp(float(ts))
    return dt.strftime(fmt)