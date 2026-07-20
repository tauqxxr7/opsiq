from fastapi.testclient import TestClient

from agents.compliance_agent import ComplianceAgent
from agents.maintenance_agent import MaintenanceAgent
from agents.pattern_agent import PatternAgent
from main import app


class AnalyticsGraph:
    async def ainvoke(self, state):
        if state["query_type"] == "maintenance":
            response = MaintenanceAgent(rows=[]).analyze(state["equipment_id"])
        elif state["query_type"] == "compliance":
            response = ComplianceAgent(rows=[]).analyze(state["standard"])
        else:
            response = PatternAgent(work_orders=[], incident_history=[]).analyze()
        return {"final_response": response}


def test_analytics_routes_validate_inputs_and_return_safe_no_data():
    with TestClient(app) as client:
        client.app.state.graph = AnalyticsGraph()
        maintenance = client.get("/api/maintenance/P-999")
        compliance = client.get("/api/compliance/audit/API-510")
        patterns = client.get("/api/patterns")
        invalid = client.get("/api/maintenance/not%20valid")
    assert maintenance.status_code == 404
    assert maintenance.json()["detail"]["no_data"] is True
    assert compliance.status_code == 200 and compliance.json()["no_data"] is True
    assert patterns.status_code == 200 and patterns.json()["records_analyzed"] == 0
    assert invalid.status_code == 422
