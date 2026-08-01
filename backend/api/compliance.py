import time

from fastapi import APIRouter, Request

from core.audit import log_query

router = APIRouter()


@router.get("/audit/{standard}")
async def audit(standard: str, request: Request):
    started = time.perf_counter()
    query = f"compliance audit {standard}"
    result = await request.app.state.graph.ainvoke(
        {"query": query, "query_type": "compliance", "standard": standard}
    )
    response = result["final_response"]
    log_query(
        query_type="compliance",
        query=query,
        confidence=response.get("confidence", 0),
        citations_count=len(response.get("citations", [])),
        response_time_ms=round((time.perf_counter() - started) * 1000),
    )
    return response