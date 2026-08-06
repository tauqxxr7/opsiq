import time

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field

from core.audit import log_query
from core.permissions import Permission, authorize

router = APIRouter()


class QueryRequest(BaseModel):
    query: str = Field(min_length=3, max_length=2000)
    query_type: str | None = None
    equipment_id: str | None = None
    standard: str | None = None


@router.post("")
async def query(payload: QueryRequest, request: Request, _: dict = Depends(authorize(Permission.GENERAL_READ))):
    started = time.perf_counter()
    state = {
        "query": payload.query,
        "query_type": payload.query_type,
        "equipment_id": payload.equipment_id,
        "standard": payload.standard,
    }
    result = await request.app.state.graph.ainvoke(state)
    response = result["final_response"]
    log_query(
        query_type=result.get("query_type") or payload.query_type or "copilot",
        query=payload.query,
        confidence=response.get("confidence", 0),
        citations_count=len(response.get("citations", [])),
        response_time_ms=round((time.perf_counter() - started) * 1000),
        detected_language=response.get("detected_language_code", "en"),
    )
    return response