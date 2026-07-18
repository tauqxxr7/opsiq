from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import documents,query,maintenance,compliance,patterns
from core.config import CORS_ORIGINS
from core.orchestrator import build_graph
from services.retrieval_service import RetrievalService
@asynccontextmanager
async def lifespan(app:FastAPI):
    app.state.retrieval_service=RetrievalService();app.state.graph=build_graph(app.state.retrieval_service);yield
app=FastAPI(title="OPSIQ API",description="Industrial Knowledge Intelligence Platform",version="1.0.0",lifespan=lifespan)
app.add_middleware(CORSMiddleware,allow_origins=CORS_ORIGINS,allow_credentials=True,allow_methods=["*"],allow_headers=["*"])
app.include_router(documents.router,prefix="/api/documents",tags=["Documents"]);app.include_router(query.router,prefix="/api/query",tags=["Query"])
app.include_router(maintenance.router,prefix="/api/maintenance",tags=["Maintenance"]);app.include_router(compliance.router,prefix="/api/compliance",tags=["Compliance"]);app.include_router(patterns.router,prefix="/api/patterns",tags=["Patterns"])
@app.get("/health")
async def health():return {"status":"operational","service":"OPSIQ"}
