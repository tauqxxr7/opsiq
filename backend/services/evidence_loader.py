import json
from pathlib import Path
from typing import Any


def load_json_records(path: str | Path) -> list[dict[str, Any]]:
    """Load a JSON array, recovering complete objects when a source is partially malformed."""
    source = Path(path)
    try:
        raw = source.read_bytes()
    except OSError:
        return []

    try:
        value = json.loads(raw.decode("utf-8-sig"))
        return [row for row in value if isinstance(row, dict)] if isinstance(value, list) else []
    except (UnicodeDecodeError, json.JSONDecodeError):
        text = raw.decode("utf-8-sig", errors="ignore")

    decoder = json.JSONDecoder()
    records: list[dict[str, Any]] = []
    cursor = 0
    while cursor < len(text):
        start = text.find("{", cursor)
        if start < 0:
            break
        try:
            value, end = decoder.raw_decode(text, start)
        except json.JSONDecodeError:
            cursor = start + 1
            continue
        if isinstance(value, dict):
            records.append(value)
        cursor = end
    return records
