from fastapi.testclient import TestClient
from main import app
from services.incident_similarity import IncidentSimilarityEngine

client = TestClient(app)


def test_sensor_fleet_and_unknown_asset():
    response = client.get("/api/sensors/fleet/status")
    assert response.status_code == 200
    assert response.json()["fleet_size"] == 5
    assert client.get("/api/sensors/live/unknown").status_code == 404


def test_sensor_trend_is_bounded():
    payload = client.get("/api/sensors/trend/P-201?hours=6").json()
    assert len(payload["readings"]) == 6
    assert payload["thresholds"]["vibration_mm_s"]["warning"] == 4.5


def test_reliability_metrics_derive_from_evidence():
    response = client.get("/api/analytics/reliability")
    assert response.status_code == 200
    payload = response.json()
    assert payload["fleet_summary"]["total_failures"] == sum(item["total_failures"] for item in payload["equipment_metrics"])


def test_incident_similarity_uses_real_schema():
    results = IncidentSimilarityEngine().find_similar("elevated vibration bearing", "P-201", 3)
    assert results
    assert {"incident_id", "failure_mode", "root_cause", "similarity_score"} <= results[0].keys()
