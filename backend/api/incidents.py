from datetime import datetime, timezone
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, Field

from core.security import Role, current_user, require_roles

router = APIRouter()
IncidentSeverity = Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
IncidentStatus = Literal["OPEN", "INVESTIGATING", "MITIGATED", "CLOSED"]


class IncidentCreate(BaseModel):
    incident_id: str | None = Field(default=None, max_length=80)
    asset_id: str = Field(min_length=1, max_length=80)
    plant: str = Field(min_length=1, max_length=120)
    unit: str = Field(min_length=1, max_length=120)
    severity: IncidentSeverity
    status: IncidentStatus = "OPEN"
    reported_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    description: str = Field(min_length=5, max_length=4000)
    symptoms: list[str] = Field(default_factory=list, max_length=50)
    suspected_cause: str | None = Field(default=None, max_length=2000)
    confirmed_root_cause: str | None = Field(default=None, max_length=2000)
    downtime_minutes: int = Field(default=0, ge=0)
    cost: float = Field(default=0, ge=0)
    corrective_action: str | None = Field(default=None, max_length=4000)
    assigned_to: str | None = Field(default=None, max_length=80)
    closed_at: datetime | None = None


class IncidentUpdate(BaseModel):
    severity: IncidentSeverity | None = None
    status: IncidentStatus | None = None
    description: str | None = Field(default=None, min_length=5, max_length=4000)
    symptoms: list[str] | None = None
    suspected_cause: str | None = None
    confirmed_root_cause: str | None = None
    downtime_minutes: int | None = Field(default=None, ge=0)
    cost: float | None = Field(default=None, ge=0)
    corrective_action: str | None = None
    assigned_to: str | None = None
    closed_at: datetime | None = None


@router.get("")
async def list_incidents(request: Request, asset_id: str | None = None, plant: str | None = None, unit: str | None = None, severity: IncidentSeverity | None = None, status: IncidentStatus | None = None, limit: int = Query(50, ge=1, le=200), offset: int = Query(0, ge=0), _: dict = Depends(current_user)):
    return request.app.state.store.list_records("incidents", {"asset_id": asset_id, "plant": plant, "unit": unit, "severity": severity, "status": status}, limit, offset)


@router.post("", status_code=201)
async def create_incident(payload: IncidentCreate, request: Request, user: dict = Depends(require_roles(Role.OPERATOR, Role.SAFETY_ENGINEER, Role.SUPERVISOR, Role.PLANT_MANAGER, Role.ADMINISTRATOR))):
    data = payload.model_dump(mode="json")
    if data["incident_id"] and request.app.state.store.get_record("incidents", data["incident_id"]):
        raise HTTPException(status_code=409, detail="Incident ID already exists")
    return request.app.state.store.create_incident(data, user["username"])


@router.get("/{incident_id}")
async def get_incident(incident_id: str, request: Request, _: dict = Depends(current_user)):
    record = request.app.state.store.get_record("incidents", incident_id)
    if not record: raise HTTPException(status_code=404, detail="Incident not found")
    return record


@router.patch("/{incident_id}")
async def update_incident(incident_id: str, payload: IncidentUpdate, request: Request, _: dict = Depends(require_roles(Role.MAINTENANCE_ENGINEER, Role.RELIABILITY_ENGINEER, Role.SAFETY_ENGINEER, Role.SUPERVISOR, Role.PLANT_MANAGER, Role.ADMINISTRATOR))):
    record = request.app.state.store.update_record("incidents", incident_id, payload.model_dump(exclude_unset=True, mode="json"))
    if not record: raise HTTPException(status_code=404, detail="Incident not found")
    return record
