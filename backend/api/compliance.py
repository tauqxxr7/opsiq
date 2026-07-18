from fastapi import APIRouter,Request
router=APIRouter()
@router.get("/audit/{standard}")
async def audit(standard:str,request:Request):
    result=await request.app.state.graph.ainvoke({"query":f"compliance audit {standard}","query_type":"compliance","standard":standard})
    return result["final_response"]
