from agents.compliance_agent import ComplianceAgent
from agents.maintenance_agent import MaintenanceAgent
from agents.pattern_agent import PatternAgent


def work(record_id, date, failure="Seal", cause="Wear", severity="HIGH", downtime=6):
    return {"work_order_id": record_id, "equipment_id": "P-1", "date": date, "failure_type": failure, "root_cause": cause, "severity": severity, "downtime_hours": downtime, "symptoms": "Vibration; Heat"}


def test_maintenance_score_is_deterministic_and_traceable():
    rows = [work("WO-1", "2025-01-01"), work("WO-2", "2025-02-01"), work("WO-3", "2025-02-20"), work("WO-4", "2025-03-01")]
    first = MaintenanceAgent(records=rows).analyze("p-1")
    second = MaintenanceAgent(records=rows).analyze("P-1")
    assert first["risk_score"] == sum(item["score"] for item in first["risk_breakdown"].values())
    for analysis in MaintenanceAgent().catalog()["equipment"]:
        assert analysis["risk_score"] == round(
            sum(item["score"] for item in analysis["risk_breakdown"].values()), 2
        )
    assert first["metadata"]["analysis_id"] == second["metadata"]["analysis_id"]
    assert first["recurrence"]["trend"] == "SHRINKING"
    assert first["supporting_evidence_ids"] == ["WO-1", "WO-2", "WO-3", "WO-4"]
    assert "failure_window" not in first
    assert "predicted_component" not in first


def test_maintenance_no_data_is_not_low_risk():
    result = MaintenanceAgent(records=[work("WO-1", "2025-01-01")]).analyze("UNKNOWN")
    assert result["status"] == "no_data"
    assert "risk_level" not in result


def test_compliance_counts_and_percentage_come_from_records():
    rows = [
        {"record_id":"I-1","standard":"OISD-118","requirement":"A","status":"COMPLIANT","severity":"LOW","evidence_source":"E1","remediation":"Maintain"},
        {"record_id":"I-2","standard":"OISD-118","requirement":"B","status":"GAP","severity":"HIGH","evidence_source":"E2","remediation":"Close"},
        {"record_id":"I-3","standard":"OISD-118","requirement":"C","status":"CRITICAL","severity":"CRITICAL","evidence_source":"E3","remediation":"Stop"},
    ]
    result = ComplianceAgent(records=rows).analyze("oisd-118")
    assert result["requirements_checked"] == 3
    assert result["summary"] == {"compliant":1,"gaps":1,"critical":1}
    assert result["compliance_percentage"] == 33.33
    assert [item["record_id"] for item in result["corrective_actions"]] == ["I-3", "I-2"]


def test_pattern_analysis_uses_both_sources_and_evidence_ids():
    work_rows = [work("WO-1", "2025-01-01"), work("WO-2", "2025-02-01")]
    incidents = [{"incident_id":"INC-1","equipment_id":"P-1","date":"2025-03-01","failure_mode":"Seal","root_cause":"Wear","severity":"HIGH","condition":"Vibration"}]
    result = PatternAgent(work_orders=work_rows, incidents=incidents).analyze()
    pattern = result["patterns"][0]
    assert result["source_counts"] == {"incident_history": 1, "work_order": 2}
    assert pattern["occurrences"] == 3
    assert pattern["first_seen"] == "2025-01-01"
    assert pattern["last_seen"] == "2025-03-01"
    assert pattern["supporting_evidence_ids"] == ["INC-1", "WO-1", "WO-2"]
    assert result["metadata"]["analysis_id"] == PatternAgent(work_orders=work_rows, incidents=incidents).analyze()["metadata"]["analysis_id"]
