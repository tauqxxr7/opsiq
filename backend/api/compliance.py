from fastapi import APIRouter, Path, Request

router = APIRouter()


@router.get("/audit/{standard}")
async def audit(request: Request, standard: str = Path(min_length=2, max_length=80, pattern=r"^[A-Za-z0-9_.-]+$")):
    result = await request.app.state.graph.ainvoke({
        "query": f"compliance audit {standard}",
        "query_type": "compliance",
        "standard": standard,
    })
    return result["final_response"]
