import asyncio
from contextlib import asynccontextmanager
import logging
from pathlib import Path

from fastapi import Depends, FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware

from api import analytics, audit, auth, benchmark, compliance, documents, incidents, maintenance, patterns, query, sensors, work_orders
from core.config import CORS_ORIGINS
from core.database import OperationalStore
from core.security import current_user
from core.orchestrator import build_graph
from keepalive import ping_self
from services.document_processor import DocumentProcessor
from services.retrieval_service import RetrievalService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app_state = {"models_ready": False, "startup_error": None}


def _initialize_models_and_evidence(retrieval):
    retrieval.initialize()
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


async def load_models_background(retrieval):
    """Load ML models and bundled evidence without blocking the application event loop."""
    try:
        logger.info("Background model loading started...")
        await asyncio.to_thread(_initialize_models_and_evidence, retrieval)
        app_state["models_ready"] = True
        logger.info("Models ready. Collection: %s chunks", retrieval.count())
    except asyncio.CancelledError:
        raise
    except Exception as error:
        app_state["startup_error"] = str(error)
        logger.exception("Model loading failed")


@asynccontextmanager
async def lifespan(app: FastAPI):
    app_state.update(models_ready=False, startup_error=None)
    retrieval = RetrievalService()
    app.state.retrieval_service = retrieval
    app.state.store = OperationalStore()
    app.state.graph = build_graph(retrieval)
    model_task = asyncio.create_task(load_models_background(retrieval))
    keepalive_task = asyncio.create_task(ping_self())
    try:
        yield
    finally:
        model_task.cancel()
        keepalive_task.cancel()
        await asyncio.gather(model_task, keepalive_task, return_exceptions=True)


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
protected = [Depends(current_user)]
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(incidents.router, prefix="/api/incidents", tags=["Incidents"])
app.include_router(work_orders.router, prefix="/api/work-orders", tags=["Work Orders"])
app.include_router(documents.router, prefix="/api/documents", tags=["Documents"], dependencies=protected)
app.include_router(query.router, prefix="/api/query", tags=["Query"], dependencies=protected)
app.include_router(maintenance.router, prefix="/api/maintenance", tags=["Maintenance"], dependencies=protected)
app.include_router(compliance.router, prefix="/api/compliance", tags=["Compliance"], dependencies=protected)
app.include_router(patterns.router, prefix="/api/patterns", tags=["Patterns"], dependencies=protected)
app.include_router(benchmark.router, prefix="/api/benchmark", tags=["Benchmark"], dependencies=protected)
app.include_router(audit.router, prefix="/api/audit", tags=["Audit"], dependencies=protected)
app.include_router(sensors.router, prefix="/api/sensors", tags=["Sensors"], dependencies=protected)
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"], dependencies=protected)


@app.get("/health")
async def health():
    """Return liveness immediately, independently of background model readiness."""
    return {"status": "operational", "service": "OPSIQ"}



@app.get("/ready")
async def readiness():
    """Report whether the retrieval models completed background initialization."""
    if not app_state["models_ready"]:
        return Response(
            content='{"status":"loading","models_ready":false}',
            status_code=503,
            media_type="application/json",
        )
    return {"status": "ready", "models_ready": True}




