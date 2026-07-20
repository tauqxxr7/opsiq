from fastapi import APIRouter, HTTPException, Path, Request

router = APIRouter()


@router.get("/{equipment_id}")
async def equipment(request: Request, equipment_id: str = Path(min_length=2, max_length=40, pattern=r"^[A-Za-z0-9_-]+$")):
    result = await request.app.state.graph.ainvoke({
        "query": f"maintenance history {equipment_id}",
        "query_type": "maintenance",
        "equipment_id": equipment_id,
    })
    response = result["final_response"]
    if response.get("no_data"):
        raise HTTPException(status_code=404, detail=response)
    return response
