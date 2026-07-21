from fastapi.testclient import TestClient

from main import app


def test_specialist_endpoints_do_not_fail_on_normalized_evidence():
    with TestClient(app) as client:
        maintenance = client.get("/api/maintenance/P-201")
        compliance = client.get("/api/compliance/audit/OISD-118")
        patterns = client.get("/api/patterns")
    assert maintenance.status_code == 200
    assert compliance.status_code == 200
    assert patterns.status_code == 200


def test_unknown_equipment_returns_explicit_no_data_contract():
    with TestClient(app) as client:
        response = client.get("/api/maintenance/UNKNOWN-999")
    assert response.status_code == 200
    assert response.json()["status"] == "no_data"
    assert response.json()["evidence"] == []
    assert response.json()["limitations"]


def test_unknown_standard_returns_explicit_no_data_contract():
    with TestClient(app) as client:
        response = client.get("/api/compliance/audit/UNKNOWN-999")
    assert response.status_code == 200
    assert response.json()["status"] == "no_data"
    assert response.json()["evidence"] == []
    assert response.json()["limitations"]
