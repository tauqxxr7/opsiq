from agents.compliance_agent import ComplianceAgent

ROWS = [{"clause": "1.1", "requirement": "Valve inspected", "status": "COMPLIANT", "evidence": "IR-1"}, {"clause": "1.2", "requirement": "Alarm tested", "status": "GAP", "evidence": "IR-2"}, {"clause": "1.3", "requirement": "Shutdown proven", "status": "CRITICAL", "evidence": "IR-3"}]

def test_counts_and_actions_come_from_rows():
    result = ComplianceAgent(rows=ROWS).analyze("OISD-118")
    assert result["requirements_checked"] == 3
    assert result["summary"] == {"compliant": 1, "gaps": 1, "critical": 1}
    assert result["compliance_percentage"] == 33.33
    assert result["corrective_actions"][0]["clause"] == "1.3"
    assert result["matrix"][0]["evidence_source"] == "IR-1"
    assert "not legal compliance certification" in result["disclaimer"]

def test_changes_with_evidence_and_unknown_standard_is_empty():
    assert ComplianceAgent(rows=[{**r, "status": "COMPLIANT"} for r in ROWS]).analyze("OISD-118")["compliance_percentage"] == 100
    unknown = ComplianceAgent(rows=ROWS).analyze("API-510")
    assert unknown["no_data"] is True and unknown["requirements_checked"] == 0
