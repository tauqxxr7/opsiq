import shutil
import uuid
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, Request, UploadFile
from services.document_processor import DocumentProcessor

router = APIRouter()
UPLOADS = Path(__file__).parents[1] / "uploads"


@router.post("/upload")
async def upload(request: Request, file: UploadFile = File(...)):
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in {".pdf", ".docx"}:
        raise HTTPException(415, "Only PDF and DOCX are supported")
    UPLOADS.mkdir(exist_ok=True)
    target = UPLOADS / f"{uuid.uuid4().hex}{suffix}"
    with target.open("wb") as output:
        shutil.copyfileobj(file.file, output)
    try:
        chunks = DocumentProcessor().process(str(target))
        request.app.state.retrieval_service.add_documents(chunks)
        return {
            "status": "indexed",
            "document": file.filename,
            "chunks_indexed": len(chunks),
            "pipeline": ["Uploading", "Extracting", "Chunking", "Embedding", "Indexed"],
        }
    finally:
        target.unlink(missing_ok=True)


@router.get("/stats")
async def stats(request: Request):
    return {"chunks": request.app.state.retrieval_service.count(), "status": "operational"}
