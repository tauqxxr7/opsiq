from contextlib import asynccontextmanager
import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api import compliance, documents, maintenance, patterns, query
from core.config import CORS_ORIGINS
from core.orchestrator import build_graph
from services.document_processor import DocumentProcessor
from services.retrieval_service import RetrievalService

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    retrieval = RetrievalService()
    if retrieval.count() == 0:
        processor = DocumentProcessor()
        synthetic_directory = Path(__file__).parent / "data" / "synthetic"
        for synthetic_file in sorted(synthetic_directory.glob("*.json")):
            try:
                chunks = processor.process(synthetic_file)
                retrieval.add_documents(chunks)
                logger.info("Auto-indexed %s: %s chunks", synthetic_file.name, len(chunks))
            except Exception as error:
                logger.warning("Auto-index failed for %s: %s", synthetic_file.name, error)
    app.state.retrieval_service = retrieval
    app.state.graph = build_graph(retrieval)
    yield


app = FastAPI(
    title="OPSIQ API",
    description="Industrial Knowledge Intelligence Platform",
    version="1.0.0",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(documents.router, prefix="/api/documents", tags=["Documents"])
app.include_router(query.router, prefix="/api/query", tags=["Query"])
app.include_router(maintenance.router, prefix="/api/maintenance", tags=["Maintenance"])
app.include_router(compliance.router, prefix="/api/compliance", tags=["Compliance"])
app.include_router(patterns.router, prefix="/api/patterns", tags=["Patterns"])


@app.get("/health")
async def health():
    return {"status": "operational", "service": "OPSIQ"}