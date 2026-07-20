from agents.maintenance_agent import MaintenanceAgent

def row(identifier, date, severity="HIGH", downtime=6):
    return {"wo_id": identifier, "equipment_id": "P-201", "date": date, "failure_type": "Seal Failure", "root_cause": "Misalignment", "severity": severity, "downtime_hours": downtime}

def test_score_is_bounded_explained_and_evidence_backed():
    result = MaintenanceAgent(rows=[row("WO-1", "2025-01-01"), row("WO-2", "2025-02-01"), row("WO-3", "2025-02-20", "CRITICAL", 12)]).analyze("p-201")
    assert 0 <= result["risk_score"] <= 100
    assert result["risk_score"] == round(sum(x["score"] for x in result["risk_breakdown"].values()), 2)
    assert result["supporting_evidence_ids"] == ["WO-1", "WO-2", "WO-3"]
    assert result["metrics"]["failure_interval_days"] == [31, 19]
    assert result["metrics"]["trend_direction"] == "SHRINKING"
    assert result["confidence"] != .88 and result["failure_window"] != "3-5 days"

def test_output_changes_when_evidence_changes():
    sparse = MaintenanceAgent(rows=[row("WO-1", "2025-01-01", "LOW", 1)]).analyze("P-201")
    recurrent = MaintenanceAgent(rows=[row("WO-1", "2025-01-01"), row("WO-2", "2025-01-10"), row("WO-3", "2025-01-15"), row("WO-4", "2025-01-18")]).analyze("P-201")
    assert recurrent["risk_score"] > sparse["risk_score"]

def test_unknown_equipment_is_safe_no_data():
    result = MaintenanceAgent(rows=[row("WO-1", "2025-01-01")]).analyze("P-999")
    assert result["no_data"] is True and result["risk_score"] == 0 and result["supporting_evidence_ids"] == []
