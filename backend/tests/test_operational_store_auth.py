from datetime import datetime, timezone

from fastapi.testclient import TestClient

import core.security as security
from core.database import OperationalStore
from main import app


def incident_payload():
    return {"asset_id":"P-201","plant":"Demo Plant","unit":"Unit 01","severity":"HIGH","status":"OPEN","reported_at":datetime.now(timezone.utc).isoformat(),"description":"Elevated vibration and bearing temperature","symptoms":["vibration","heat"],"downtime_minutes":30,"cost":1200}


def test_persistent_incident_and_work_order_lifecycle(tmp_path):
    with TestClient(app) as client:
        client.app.state.store = OperationalStore(tmp_path / "opsiq.db")
        incident = client.post("/api/incidents", json=incident_payload())
        assert incident.status_code == 201
        incident_id = incident.json()["incident_id"]
        assert client.get("/api/incidents", params={"asset_id":"P-201"}).json()["total"] == 1
        work = client.post("/api/work-orders", json={"incident_id":incident_id,"asset_id":"P-201","priority":"HIGH","status":"PENDING_APPROVAL","recommended_action":"Inspect and align the pump coupling","required_parts":["coupling kit"],"required_skills":["Maintenance Engineer"]})
        assert work.status_code == 201
        approved = client.post(f"/api/work-orders/{work.json()['work_order_id']}/approve")
        assert approved.status_code == 200
        assert approved.json()["status"] == "APPROVED"
        assert approved.json()["approval_history"][0]["actor"] == "system"


def test_login_refresh_and_operator_permission(tmp_path, monkeypatch):
    store = OperationalStore(tmp_path / "auth.db")
    store.create_user({"username":"operator1","display_name":"Demo Operator","password":"long-secure-password","role":"Operator"})
    monkeypatch.setattr(security, "JWT_SECRET", "test-secret-that-is-long-enough-for-hmac")
    monkeypatch.setattr(security, "AUTH_REQUIRED", True)
    with TestClient(app) as client:
        client.app.state.store = store
        login = client.post("/api/auth/login", json={"username":"operator1","password":"long-secure-password"})
        assert login.status_code == 200
        tokens = login.json()
        refreshed = client.post("/api/auth/refresh", json={"refresh_token":tokens["refresh_token"]})
        assert refreshed.status_code == 200
        headers={"Authorization":f"Bearer {tokens['access_token']}"}
        assert client.get("/api/auth/me", headers=headers).json()["role"] == "Operator"
        assert client.post("/api/incidents", json=incident_payload(), headers=headers).status_code == 201
        denied = client.post("/api/work-orders", json={"asset_id":"P-201","priority":"HIGH","recommended_action":"Inspect coupling"}, headers=headers)
        assert denied.status_code == 403
