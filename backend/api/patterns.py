from fastapi import APIRouter,Request
router=APIRouter()
@router.get("")
async def patterns(request:Request):
    result=await request.app.state.graph.ainvoke({"query":"recurring systemic failure patterns","query_type":"pattern"})
    return result["final_response"]
