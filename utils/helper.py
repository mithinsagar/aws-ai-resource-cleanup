"""
General-purpose helper functions.
Author: Mithin Sagar S
"""

import datetime
from dateutil import tz


def days_since(timestamp):
    if timestamp is None:
        return float("inf")
    now = datetime.datetime.now(datetime.timezone.utc)
    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=tz.UTC)
    delta = now - timestamp
    return delta.days


def format_timestamp(timestamp):
    if timestamp is None:
        return "N/A"
    return timestamp.strftime("%Y-%m-%d %H:%M:%S UTC")


def has_protected_tag(tags, protected_keys):
    if not tags:
        return False
    for tag in tags:
        key = tag.get("Key", "").lower()
        value = tag.get("Value", "").lower()
        if key in protected_keys or value in protected_keys:
            return True
    return False


def bytes_to_human(size_bytes):
    if size_bytes == 0:
        return "0 B"
    units = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(units) - 1:
        size_bytes /= 1024
        i += 1
    return f"{size_bytes:.2f} {units[i]}"
