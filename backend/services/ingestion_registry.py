"""Persistent metadata registry for uploaded evidence documents."""
import json
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock

from core.config import CHROMA_DB_PATH


class IngestionRegistryError(RuntimeError):
    """Raised when the persistent ingestion manifest is unreadable or invalid."""


class IngestionRegistry:
    _lock = Lock()

    def __init__(self, path=None):
        self.path = Path(path) if path else Path(CHROMA_DB_PATH) / "ingestion_manifest.json"

    def list(self):
        if not self.path.exists():
            return []
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8-sig"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise IngestionRegistryError("The ingestion manifest cannot be read safely") from exc
        if not isinstance(payload, list) or not all(isinstance(item, dict) for item in payload):
            raise IngestionRegistryError("The ingestion manifest must contain a JSON record array")
        return payload

    def contains(self, content_hash):
        return any(item.get("content_hash") == content_hash for item in self.list())

    def add(self, *, content_hash, filename, doc_type, chunks, pages):
        record = {
            "content_hash": content_hash,
            "filename": filename,
            "doc_type": doc_type,
            "chunks": chunks,
            "pages": pages,
            "status": "indexed",
            "indexed_at": datetime.now(timezone.utc).isoformat(),
        }
        with self._lock:
            current = self.list()
            if any(item.get("content_hash") == content_hash for item in current):
                return None
            self.path.parent.mkdir(parents=True, exist_ok=True)
            temporary = self.path.with_suffix(".tmp")
            temporary.write_text(json.dumps([*current, record], indent=2), encoding="utf-8")
            temporary.replace(self.path)
        return record
