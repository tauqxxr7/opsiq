"""Persistent metadata registry for uploaded evidence documents."""
import json
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock

from core.config import CHROMA_DB_PATH


class IngestionRegistry:
    def __init__(self, path=None):
        self.path = Path(path) if path else Path(CHROMA_DB_PATH) / "ingestion_manifest.json"
        self._lock = Lock()

    def list(self):
        if not self.path.exists(): return []
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8-sig"))
        except (OSError, UnicodeError, json.JSONDecodeError):
            return []
        return payload if isinstance(payload, list) else []

    def contains(self, content_hash):
        return any(item.get("content_hash") == content_hash for item in self.list())

    def add(self, *, content_hash, filename, doc_type, chunks, pages):
        record = {"content_hash": content_hash, "filename": filename, "doc_type": doc_type, "chunks": chunks, "pages": pages, "status": "indexed", "indexed_at": datetime.now(timezone.utc).isoformat()}
        with self._lock:
            current = self.list()
            if any(item.get("content_hash") == content_hash for item in current): return None
            self.path.parent.mkdir(parents=True, exist_ok=True)
            temporary = self.path.with_suffix(".tmp")
            temporary.write_text(json.dumps([*current, record], indent=2), encoding="utf-8")
            temporary.replace(self.path)
        return record
