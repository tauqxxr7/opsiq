from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

router = APIRouter()


class QueryRequest(BaseModel):
    query: str = Field(min_length=3, max_length=2000)
    query_type: str | None = Field(default=None, pattern=r"^(copilot|maintenance|compliance|pattern)$")
    equipment_id: str | None = Field(default=None, min_length=2, max_length=40, pattern=r"^[A-Za-z0-9_-]+$")
    standard: str | None = Field(default=None, min_length=2, max_length=80, pattern=r"^[A-Za-z0-9_.-]+$")


@router.post("")
async def query(payload: QueryRequest, request: Request):
    state = {"query": payload.query, "query_type": payload.query_type,
             "equipment_id": payload.equipment_id, "standard": payload.standard}
    result = await request.app.state.graph.ainvoke(state)
    return result["final_response"]
