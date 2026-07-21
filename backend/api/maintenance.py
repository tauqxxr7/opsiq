from fastapi import APIRouter, Request

from agents.maintenance_agent import MaintenanceAgent

router = APIRouter()


@router.get("")
async def catalog():
    return MaintenanceAgent().catalog()


@router.get("/{equipment_id}")
async def equipment(equipment_id: str, request: Request):
    result = await request.app.state.graph.ainvoke({"query": f"maintenance history {equipment_id}", "query_type": "maintenance", "equipment_id": equipment_id})
    return result["final_response"]
