import time

from fastapi import APIRouter, Depends, Request

from agents.maintenance_agent import MaintenanceAgent
from core.audit import log_query
from core.permissions import Permission, authorize

router = APIRouter()


@router.get("")
async def catalog(_: dict = Depends(authorize(Permission.GENERAL_READ))):
    return MaintenanceAgent().catalog()


@router.get("/{equipment_id}")
async def equipment(equipment_id: str, request: Request, _: dict = Depends(authorize(Permission.GENERAL_READ))):
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

@router.post("/incidents/similar")
async def find_similar_incidents(payload: dict, _: dict = Depends(authorize(Permission.GENERAL_READ))):
    from services.incident_similarity import IncidentSimilarityEngine
    results = IncidentSimilarityEngine().find_similar(payload.get("description", ""), payload.get("equipment_id"), payload.get("top_k", 3))
    return {"query": payload.get("description", ""), "equipment_id": payload.get("equipment_id"), "similar_incidents": results, "count": len(results)}


@router.post("/workorder/generate/{equipment_id}")
async def generate_work_order(equipment_id: str, _: dict = Depends(authorize(Permission.WORK_ORDER_CREATE))):
    from agents.workorder_agent import WorkOrderAgent
    from services.incident_similarity import IncidentSimilarityEngine
    analysis = MaintenanceAgent().analyze(equipment_id)
    if analysis["status"] == "no_data":
        return analysis
    similar = IncidentSimilarityEngine().find_similar(analysis["dominant_failure_mode"], equipment_id, 2)
    return WorkOrderAgent().generate_work_order(equipment_id.upper(), analysis, similar)
