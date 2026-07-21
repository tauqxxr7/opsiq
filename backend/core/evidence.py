"""Validated loading and traceability helpers for OPSIQ evidence datasets."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, TypeVar

from pydantic import BaseModel, ConfigDict, Field, ValidationError


class EvidenceLoadError(RuntimeError):
    """Raised when an evidence file cannot be decoded or validated safely."""


class EvidenceRecord(BaseModel):
    model_config = ConfigDict(extra="allow")


class WorkOrderRecord(EvidenceRecord):
    work_order_id: str = Field(validation_alias="wo_id")
    equipment_id: str
    date: str
    failure_type: str
    root_cause: str
    severity: str
    downtime_hours: float = Field(ge=0)


class InspectionRecord(EvidenceRecord):
    record_id: str
    standard: str
    requirement: str
    status: str
    severity: str
    evidence_source: str
    remediation: str


class IncidentRecord(EvidenceRecord):
    incident_id: str
    equipment_id: str
    date: str
    failure_mode: str
    root_cause: str
    severity: str


RecordT = TypeVar("RecordT", bound=EvidenceRecord)


def load_records(path: Path, schema: type[RecordT]) -> list[RecordT]:
    """Load a JSON array with BOM tolerance and strict record validation."""
    try:
        payload: Any = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise EvidenceLoadError(f"Unable to load evidence file {path.name}: {exc}") from exc
    if not isinstance(payload, list):
        raise EvidenceLoadError(f"Evidence file {path.name} must contain a JSON array")
    try:
        return [schema.model_validate(record) for record in payload]
    except ValidationError as exc:
        raise EvidenceLoadError(f"Invalid record in {path.name}: {exc}") from exc


def dataset_sha256(*paths: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(paths, key=lambda item: item.as_posix()):
        digest.update(path.name.encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def deterministic_analysis_id(
    analysis_type: str,
    normalized_inputs: dict[str, Any],
    dataset_hash: str,
    methodology_version: str,
) -> str:
    payload = json.dumps(
        {
            "analysis_type": analysis_type,
            "inputs": normalized_inputs,
            "dataset_hash": dataset_hash,
            "methodology_version": methodology_version,
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:20]

