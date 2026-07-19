from fastapi.testclient import TestClient

from main import app


def test_health_returns_operational_status():
    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "operational", "service": "OPSIQ"}


def test_startup_does_not_require_indexed_documents():
    with TestClient(app) as client:
        assert client.app.state.retrieval_service.initialized is False
        assert client.app.state.graph.initialized is False
        assert client.get("/health").status_code == 200
