import pytest
from fastapi.testclient import TestClient
import api.documents as documents_api
from main import app

class FakeRetrieval:
    initialized=False
    def __init__(self):self.indexed=[]
    def add_documents(self,chunks):self.indexed.extend(chunks)
    def count(self):return len(self.indexed)
class FakeRegistry:
    records=[]
    def list(self):return list(self.records)
    def contains(self,digest):return any(row["content_hash"]==digest for row in self.records)
    def add(self,**record):
        if self.contains(record["content_hash"]):return None
        stored={**record,"status":"indexed","indexed_at":"2026-01-01T00:00:00+00:00"};self.records.append(stored);return stored
class GoodProcessor:
    def process(self,*args,display_name,content_hash,**kwargs):return [{"text":"Evidence text long enough to form a grounded chunk for testing.","doc_name":display_name,"page":1,"section":"General","doc_type":"Safety Standard","chunk_id":f"{content_hash[:16]}_p1_c0"}]
def setup(monkeypatch):
    FakeRegistry.records=[];monkeypatch.setattr(documents_api,"IngestionRegistry",FakeRegistry);monkeypatch.setattr(documents_api,"DocumentProcessor",GoodProcessor)

def test_upload_status_contracts_and_inventory(monkeypatch):
    setup(monkeypatch)
    with TestClient(app) as client:
        client.app.state.retrieval_service=FakeRetrieval()
        unsupported=client.post("/api/documents/upload",files={"file":("notes.txt",b"text","text/plain")})
        empty=client.post("/api/documents/upload",files={"file":("empty.pdf",b"","application/pdf")})
        mismatch=client.post("/api/documents/upload",files={"file":("fake.pdf",b"not pdf","application/pdf")})
        valid=client.post("/api/documents/upload",files={"file":("standard.pdf",b"%PDF-1.7 evidence","application/pdf")})
        duplicate=client.post("/api/documents/upload",files={"file":("copy.pdf",b"%PDF-1.7 evidence","application/pdf")})
        inventory=client.get("/api/documents")
    assert unsupported.status_code==415;assert empty.status_code==422;assert mismatch.status_code==422
    assert valid.status_code==200 and valid.json()["status"]=="indexed";assert duplicate.status_code==409
    assert inventory.json()["document_count"]==1;assert inventory.json()["documents"][0]["filename"]=="standard.pdf"

def test_upload_over_size_is_413(monkeypatch):
    setup(monkeypatch);monkeypatch.setattr(documents_api,"MAX_UPLOAD_SIZE_MB",0)
    with TestClient(app) as client:response=client.post("/api/documents/upload",files={"file":("large.pdf",b"%PDF data","application/pdf")})
    assert response.status_code==413

def test_corrupt_parser_result_is_422(monkeypatch):
    setup(monkeypatch)
    class CorruptProcessor:
        def process(self,*args,**kwargs):raise ValueError("corrupt")
    monkeypatch.setattr(documents_api,"DocumentProcessor",CorruptProcessor)
    with TestClient(app) as client:response=client.post("/api/documents/upload",files={"file":("corrupt.pdf",b"%PDF broken","application/pdf")})
    assert response.status_code==422;assert "corrupt" in response.json()["detail"].lower()


def test_corrupt_registry_fails_closed(tmp_path):
    from services.ingestion_registry import IngestionRegistry, IngestionRegistryError
    manifest = tmp_path / "manifest.json"
    manifest.write_text("not-json", encoding="utf-8")
    with pytest.raises(IngestionRegistryError, match="cannot be read safely"):
        IngestionRegistry(manifest).list()
