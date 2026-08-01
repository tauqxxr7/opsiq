import json
import logging
import threading
from collections import deque
from datetime import datetime, timezone

audit_logger = logging.getLogger("opsiq.audit")
audit_logger.setLevel(logging.INFO)

_entries = deque(maxlen=20)
_entries_lock = threading.Lock()


def log_query(
    query_type: str,
    query: str,
    confidence: float,
    citations_count: int,
    response_time_ms: int,
    detected_language: str = "en",
):
    """Record non-content query telemetry in the process-local audit trail."""
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "query_type": query_type,
        "query_length": len(query),
        "confidence": round(float(confidence or 0), 3),
        "citations_returned": int(citations_count),
        "response_time_ms": int(response_time_ms),
        "language": detected_language,
    }
    with _entries_lock:
        _entries.append(entry)
    audit_logger.info(json.dumps(entry, separators=(",", ":")))
    return entry


def recent_entries():
    with _entries_lock:
        return list(reversed(_entries))
