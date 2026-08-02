from datetime import datetime, timezone
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, Field

from core.security import Role, current_user, require_roles

router = APIRouter()
Priority = Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
WorkStatus = Literal["DRAFT", "PENDING_APPROVAL", "APPROVED", "ASSIGNED", "IN_PROGRESS", "WAITING_FOR_PARTS", "COMPLETED", "CLOSED", "CANCELLED"]


class WorkOrderCreate(BaseModel):
    work_order_id: str | None = Field(default=None, max_length=80)
    incident_id: str | None = Field(default=None, max_length=80)
    asset_id: str = Field(min_length=1, max_length=80)
    priority: Priority
    status: WorkStatus = "DRAFT"
    recommended_action: str = Field(min_length=5, max_length=4000)
    required_parts: list[str] = Field(default_factory=list)
    required_skills: list[str] = Field(default_factory=list)
    assigned_to: str | None = Field(default=None, max_length=80)
    created_at: datetime | None = None
    approved_at: datetime | None = None
    completed_at: datetime | None = None
    approval_history: list[dict] = Field(default_factory=list)
    completion_notes: str | None = Field(default=None, max_length=4000)


class WorkOrderUpdate(BaseModel):
    priority: Priority | None = None
    status: WorkStatus | None = None
    recommended_action: str | None = Field(default=None, min_length=5, max_length=4000)
    required_parts: list[str] | None = None
    required_skills: list[str] | None = None
    assigned_to: str | None = None
    completion_notes: str | None = None


@router.get("")
async def list_work_orders(request: Request, incident_id: str | None = None, asset_id: str | None = None, priority: Priority | None = None, status: WorkStatus | None = None, limit: int = Query(50, ge=1, le=200), offset: int = Query(0, ge=0), _: dict = Depends(current_user)):
    return request.app.state.store.list_records("work_orders", {"incident_id": incident_id, "asset_id": asset_id, "priority": priority, "status": status}, limit, offset)


@router.post("", status_code=201)
async def create_work_order(payload: WorkOrderCreate, request: Request, user: dict = Depends(require_roles(Role.MAINTENANCE_ENGINEER, Role.RELIABILITY_ENGINEER, Role.SUPERVISOR, Role.PLANT_MANAGER, Role.ADMINISTRATOR))):
    if payload.incident_id and not request.app.state.store.get_record("incidents", payload.incident_id):
        raise HTTPException(status_code=422, detail="Linked incident does not exist")
    if payload.work_order_id and request.app.state.store.get_record("work_orders", payload.work_order_id):
        raise HTTPException(status_code=409, detail="Work-order ID already exists")
    return request.app.state.store.create_work_order(payload.model_dump(mode="json"), user["username"])


@router.get("/{work_order_id}")
async def get_work_order(work_order_id: str, request: Request, _: dict = Depends(current_user)):
    record=request.app.state.store.get_record("work_orders", work_order_id)
    if not record: raise HTTPException(status_code=404, detail="Work order not found")
    return record


@router.patch("/{work_order_id}")
async def update_work_order(work_order_id: str, payload: WorkOrderUpdate, request: Request, _: dict = Depends(require_roles(Role.MAINTENANCE_ENGINEER, Role.SUPERVISOR, Role.PLANT_MANAGER, Role.ADMINISTRATOR))):
    record=request.app.state.store.update_record("work_orders", work_order_id, payload.model_dump(exclude_unset=True))
    if not record: raise HTTPException(status_code=404, detail="Work order not found")
    return record


@router.post("/{work_order_id}/approve")
async def approve_work_order(work_order_id: str, request: Request, user: dict = Depends(require_roles(Role.SUPERVISOR, Role.PLANT_MANAGER, Role.ADMINISTRATOR))):
    record=request.app.state.store.get_record("work_orders", work_order_id)
    if not record: raise HTTPException(status_code=404, detail="Work order not found")
    history=[*record["approval_history"], {"actor": user["username"], "action": "APPROVED", "at": datetime.now(timezone.utc).isoformat()}]
    return request.app.state.store.update_record("work_orders", work_order_id, {"status":"APPROVED", "approved_at":datetime.now(timezone.utc).isoformat(), "approval_history":history})


class CompletionRequest(BaseModel):
    completion_notes: str = Field(min_length=3, max_length=4000)


@router.post("/{work_order_id}/complete")
async def complete_work_order(work_order_id: str, payload: CompletionRequest, request: Request, _: dict = Depends(require_roles(Role.MAINTENANCE_ENGINEER, Role.SUPERVISOR, Role.PLANT_MANAGER, Role.ADMINISTRATOR))):
    record=request.app.state.store.get_record("work_orders", work_order_id)
    if not record: raise HTTPException(status_code=404, detail="Work order not found")
    return request.app.state.store.update_record("work_orders", work_order_id, {"status":"COMPLETED", "completed_at":datetime.now(timezone.utc).isoformat(), "completion_notes":payload.completion_notes})
