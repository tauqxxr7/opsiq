import hashlib
import uuid
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, Request, UploadFile

from core.config import MAX_UPLOAD_SIZE_MB
from services.document_processor import DocumentProcessor
from services.ingestion_registry import IngestionRegistry

router = APIRouter()
UPLOADS = Path(__file__).parents[1] / "uploads"
SUPPORTED = {".pdf": b"%PDF", ".docx": b"PK"}


@router.post("/upload")
async def upload(request: Request, file: UploadFile = File(...)):
    filename = Path((file.filename or "").replace("\\", "/")).name
    suffix = Path(filename).suffix.lower()
    if suffix not in SUPPORTED:
        raise HTTPException(415, "Only PDF and DOCX are supported")
    UPLOADS.mkdir(exist_ok=True)
    target = UPLOADS / f"{uuid.uuid4().hex}{suffix}"
    digest = hashlib.sha256(); total = 0; limit = MAX_UPLOAD_SIZE_MB * 1024 * 1024
    try:
        with target.open("wb") as output:
            while chunk := await file.read(1024 * 1024):
                total += len(chunk)
                if total > limit: raise HTTPException(413, f"File exceeds the {MAX_UPLOAD_SIZE_MB} MB upload limit")
                digest.update(chunk); output.write(chunk)
        if total == 0: raise HTTPException(422, "Uploaded document is empty")
        signature = target.read_bytes()[:4]
        if not signature.startswith(SUPPORTED[suffix]): raise HTTPException(422, "File content does not match its extension")
        content_hash = digest.hexdigest(); registry = IngestionRegistry()
        if registry.contains(content_hash): raise HTTPException(409, "An identical document is already indexed")
        try:
            chunks = DocumentProcessor().process(target, display_name=filename, content_hash=content_hash)
        except HTTPException: raise
        except Exception as exc:
            raise HTTPException(422, "Document is corrupt or could not be parsed") from exc
        if not chunks: raise HTTPException(422, "Document contains no extractable text")
        request.app.state.retrieval_service.add_documents(chunks)
        record = registry.add(content_hash=content_hash, filename=filename, doc_type=chunks[0]["doc_type"], chunks=len(chunks), pages=len({chunk["page"] for chunk in chunks}))
        if record is None: raise HTTPException(409, "An identical document is already indexed")
        return {"status": "indexed", "document": filename, "content_hash": content_hash, "chunks_indexed": len(chunks), "pages": record["pages"], "doc_type": record["doc_type"], "indexed_at": record["indexed_at"], "pipeline": ["Uploading", "Extracting", "Chunking", "Embedding", "Indexed"]}
    finally:
        await file.close(); target.unlink(missing_ok=True)


@router.get("")
async def inventory():
    documents = IngestionRegistry().list()
    return {"status": "ok", "documents": documents, "document_count": len(documents), "chunks": sum(item.get("chunks",0) for item in documents)}


@router.get("/stats")
async def stats(request: Request):
    documents = IngestionRegistry().list()
    return {"chunks": request.app.state.retrieval_service.count(), "documents": len(documents), "status": "operational"}
