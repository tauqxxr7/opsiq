import time

from fastapi import APIRouter, Depends, Request

from core.audit import log_query
from core.permissions import Permission, authorize

router = APIRouter()


@router.get("")
async def patterns(request: Request, _: dict = Depends(authorize(Permission.PATTERNS_READ))):
    started = time.perf_counter()
    query = "recurring systemic failure patterns"
    result = await request.app.state.graph.ainvoke(
        {"query": query, "query_type": "pattern"}
    )
    response = result["final_response"]
    log_query(
        query_type="pattern",
        query=query,
        confidence=response.get("confidence", 0),
        citations_count=len(response.get("citations", [])),
        response_time_ms=round((time.perf_counter() - started) * 1000),
    )
    return response