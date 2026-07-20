from agents.pattern_agent import PatternAgent
from services.evidence_loader import load_json_records

WORK = [{"wo_id": "WO-1", "equipment_id": "P-1", "failure_type": "Seal", "root_cause": "Alignment", "date": "2025-01-01", "downtime_hours": 12, "symptoms": "Heat;Noise"}, {"wo_id": "WO-2", "equipment_id": "P-1", "failure_type": "Seal", "root_cause": "Alignment", "date": "2025-02-01", "downtime_hours": 10, "symptoms": "Heat"}]
INCIDENTS = [{"incident_id": "INC-1", "equipment_id": "P-2", "failure_mode": "Bearing", "root_cause": "Alignment", "date": "2025-03-01", "condition": "Heat"}]

def test_aggregates_sources_and_graph_evidence():
    result = PatternAgent(work_orders=WORK, incident_history=INCIDENTS).analyze()
    assert result["records_analyzed"] == 3
    assert result["source_counts"] == {"incident_history": 1, "work_order": 2}
    assert result["patterns"][0]["supporting_evidence_ids"] == ["WO-1", "WO-2"]
    assert result["recurring_root_causes"][0]["equipment_ids"] == ["P-1", "P-2"]
    assert result["high_downtime_clusters"][0]["cumulative_downtime_hours"] == 22
    assert result["knowledge_graph"]["metrics"]["edge_count"] > 0

def test_empty_input_is_safe():
    result = PatternAgent(work_orders=[], incident_history=[]).analyze()
    assert result["no_data"] is True and result["patterns"] == [] and result["confidence"] == 0

def test_tolerant_loader_recovers_valid_incident_records():
    rows = load_json_records("data/synthetic/incident_history.json")
    assert len(rows) >= 11 and rows[0]["incident_id"] == "INC-2025-001"
