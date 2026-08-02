from fastapi import APIRouter, Depends

from core.audit import recent_entries
from core.permissions import Permission, authorize

router = APIRouter()


@router.get("/recent")
async def recent_audit_entries(_: dict = Depends(authorize(Permission.AUDIT_READ))):
    entries = recent_entries()
    return {"entries": entries, "count": len(entries), "persistence": "process_memory"}
