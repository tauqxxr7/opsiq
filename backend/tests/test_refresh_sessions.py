import sqlite3

from fastapi.testclient import TestClient

import core.security as security
from core.database import OperationalStore
from main import app

PASSWORD = "long-secure-password"
SECRET = "test-secret-that-is-long-enough-for-hmac"


def auth_client(tmp_path, monkeypatch):
    store = OperationalStore(tmp_path / "auth.db")
    store.create_user({"username": "engineer", "display_name": "Demo Engineer", "password": PASSWORD, "role": "Maintenance Engineer"})
    monkeypatch.setattr(security, "JWT_SECRET", SECRET)
    monkeypatch.setattr(security, "AUTH_REQUIRED", True)
    client = TestClient(app)
    client.app.state.store = store
    return client, store


def login(client, username="engineer"):
    response = client.post("/api/auth/login", json={"username": username, "password": PASSWORD})
    assert response.status_code == 200
    return response.json()


def test_refresh_rotation_and_replay_protection(tmp_path, monkeypatch):
    client, _ = auth_client(tmp_path, monkeypatch)
    first = login(client)
    rotated = client.post("/api/auth/refresh", json={"refresh_token": first["refresh_token"]})
    assert rotated.status_code == 200
    second = rotated.json()
    assert second["refresh_token"] != first["refresh_token"]
    assert security.decode_token(second["refresh_token"], "refresh")["jti"] != security.decode_token(first["refresh_token"], "refresh")["jti"]
    assert client.post("/api/auth/refresh", json={"refresh_token": first["refresh_token"]}).status_code == 401
    assert client.post("/api/auth/refresh", json={"refresh_token": second["refresh_token"]}).status_code == 200


def test_refresh_sessions_store_no_raw_tokens(tmp_path, monkeypatch):
    client, store = auth_client(tmp_path, monkeypatch)
    token = login(client)["refresh_token"]
    with sqlite3.connect(store.path) as db:
        stored = db.execute("SELECT jti_hash FROM refresh_sessions").fetchone()[0]
    assert token not in stored
    assert len(stored) == 64


def test_logout_is_idempotent_and_revokes_refresh(tmp_path, monkeypatch):
    client, _ = auth_client(tmp_path, monkeypatch)
    token = login(client)["refresh_token"]
    payload = {"refresh_token": token}
    assert client.post("/api/auth/logout", json=payload).json() == {"status": "logged_out"}
    assert client.post("/api/auth/logout", json=payload).json() == {"status": "logged_out"}
    assert client.post("/api/auth/refresh", json=payload).status_code == 401


def test_expired_refresh_token_fails(tmp_path, monkeypatch):
    client, store = auth_client(tmp_path, monkeypatch)
    jti = "expired-session"
    store.create_refresh_session("engineer", jti, 0)
    token = security.create_token("engineer", "Maintenance Engineer", "refresh", -1, jti)
    assert client.post("/api/auth/refresh", json={"refresh_token": token}).status_code == 401


def test_disabled_user_cannot_refresh(tmp_path, monkeypatch):
    client, store = auth_client(tmp_path, monkeypatch)
    token = login(client)["refresh_token"]
    store.update_user("engineer", {"active": False})
    assert client.post("/api/auth/refresh", json={"refresh_token": token}).status_code == 401


def test_role_change_invalidates_sessions(tmp_path, monkeypatch):
    client, store = auth_client(tmp_path, monkeypatch)
    store.create_user({"username": "admin", "display_name": "Administrator", "password": PASSWORD, "role": "Administrator"})
    token = login(client)["refresh_token"]
    admin = login(client, "admin")
    response = client.patch(
        "/api/auth/users/engineer",
        json={"role": "Reliability Engineer"},
        headers={"Authorization": f"Bearer {admin['access_token']}"},
    )
    assert response.status_code == 200
    assert response.json()["role"] == "Reliability Engineer"
    assert client.post("/api/auth/refresh", json={"refresh_token": token}).status_code == 401


def test_administrator_can_revoke_all_user_sessions(tmp_path, monkeypatch):
    client, store = auth_client(tmp_path, monkeypatch)
    store.create_user({"username": "admin", "display_name": "Administrator", "password": PASSWORD, "role": "Administrator"})
    user_token = login(client)["refresh_token"]
    admin = login(client, "admin")
    response = client.post(
        "/api/auth/users/engineer/revoke-sessions",
        headers={"Authorization": f"Bearer {admin['access_token']}"},
    )
    assert response.status_code == 200
    assert response.json()["sessions_revoked"] == 1
    assert client.post("/api/auth/refresh", json={"refresh_token": user_token}).status_code == 401