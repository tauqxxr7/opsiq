from fastapi import APIRouter

from core.audit import recent_entries

router = APIRouter()


@router.get("/recent")
async def recent_audit_entries():
    entries = recent_entries()
    return {"entries": entries, "count": len(entries), "persistence": "process_memory"}
