import json
from pathlib import Path

import pytest

from core.evidence import EvidenceLoadError, IncidentRecord, WorkOrderRecord, load_records


def test_loader_accepts_utf8_bom(tmp_path: Path):
    path = tmp_path / "work_orders.json"
    payload = [{
        "wo_id": "WO-1", "equipment_id": "P-1", "date": "2025-01-01",
        "failure_type": "Seal", "root_cause": "Wear", "severity": "LOW",
        "downtime_hours": 1,
    }]
    path.write_bytes(b"\xef\xbb\xbf" + json.dumps(payload).encode("utf-8"))
    records = load_records(path, WorkOrderRecord)
    assert records[0].work_order_id == "WO-1"


def test_corrupted_json_fails_closed_without_partial_records(tmp_path: Path):
    path = tmp_path / "incidents.json"
    path.write_bytes(b'[{"incident_id":"INC-1"}\xff]')
    with pytest.raises(EvidenceLoadError, match="Unable to load evidence file"):
        load_records(path, IncidentRecord)


def test_recovered_runtime_incidents_are_exactly_independently_valid_records():
    path = Path(__file__).parents[1] / "data/synthetic/incident_history.json"
    records = load_records(path, IncidentRecord)
    assert len(records) == 11
    assert records[0].incident_id == "INC-2025-001"
    assert records[-1].incident_id == "INC-2025-011"
