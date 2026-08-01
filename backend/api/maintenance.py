import time

from fastapi import APIRouter, Request

from agents.maintenance_agent import MaintenanceAgent
from core.audit import log_query

router = APIRouter()


@router.get("")
async def catalog():
    return MaintenanceAgent().catalog()


@router.get("/{equipment_id}")
async def equipment(equipment_id: str, request: Request):
    started = time.perf_counter()
    query = f"maintenance history {equipment_id}"
    result = await request.app.state.graph.ainvoke(
        {"query": query, "query_type": "maintenance", "equipment_id": equipment_id}
    )
    response = result["final_response"]
    log_query(
        query_type="maintenance",
        query=query,
        confidence=response.get("confidence", 0),
        citations_count=len(response.get("citations", [])),
        response_time_ms=round((time.perf_counter() - started) * 1000),
    )
    return response