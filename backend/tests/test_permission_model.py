from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
import pytest

import core.security as security
from core.permissions import PERMISSION_ROLES, Permission, authorize
from core.security import Role, current_user
from main import app

EXPECTED_SPECIALIST = {
    "/api/compliance/audit/{standard}": Permission.COMPLIANCE_READ,
    "/api/patterns": Permission.PATTERNS_READ,
    "/api/benchmark/run": Permission.BENCHMARK_EXECUTE,
    "/api/audit/recent": Permission.AUDIT_READ,
    "/api/documents/upload": Permission.DOCUMENT_UPLOAD,
    "/api/maintenance/workorder/generate/{equipment_id}": Permission.WORK_ORDER_CREATE,
}


def permission_of(route):
    values = [getattr(item.call, "permission", None) for item in route.dependant.dependencies]
    return next((value for value in values if value), None)


def protected_routes():
    for route in app.routes:
        if getattr(route, "path", "").startswith("/api/"):
            yield route.path, route


def test_every_protected_api_route_declares_a_canonical_permission():
    public = {("/api/auth/login", "POST"), ("/api/auth/refresh", "POST"), ("/api/auth/logout", "POST")}
    routes = list(protected_routes())
    for path, route in routes:
        for method in route.methods - {"HEAD", "OPTIONS"}:
            if (path, method) not in public:
                assert permission_of(route), f"{method} {path} has no explicit canonical permission"
    by_path = {path: permission_of(route) for path, route in routes}
    assert {path: by_path[path] for path in EXPECTED_SPECIALIST} == {path: permission.value for path, permission in EXPECTED_SPECIALIST.items()}


@pytest.mark.parametrize("role", list(Role))
def test_all_eight_roles_match_canonical_permission_matrix(role):
    test_app = FastAPI()
    test_app.dependency_overrides[current_user] = lambda: {"username": "test", "display_name": "Test", "role": role.value}
    for permission in Permission:
        async def endpoint(_=Depends(authorize(permission))):
            return {"allowed": True}
        test_app.add_api_route(f"/{permission.value}", endpoint)
    client = TestClient(test_app)
    for permission, allowed_roles in PERMISSION_ROLES.items():
        response = client.get(f"/{permission.value}")
        assert response.status_code == (200 if role in allowed_roles else 403), f"{role.value} / {permission.value}"


def test_authentication_failures_remain_401(monkeypatch):
    test_app = FastAPI()
    test_app.add_api_route("/protected", lambda _=Depends(authorize(Permission.GENERAL_READ)): {"ok": True})
    monkeypatch.setattr(security, "AUTH_REQUIRED", True)
    monkeypatch.setattr(security, "JWT_SECRET", "test-secret-that-is-long-enough-for-hmac")
    client = TestClient(test_app)
    assert client.get("/protected").status_code == 401
    assert client.get("/protected", headers={"Authorization": "Bearer invalid"}).status_code == 401