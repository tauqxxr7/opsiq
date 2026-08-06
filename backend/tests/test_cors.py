from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.testclient import TestClient

OPSIQ_PREVIEW_REGEX = r"^https://(?:opsiq-one\.vercel\.app|opsiq-(?:[a-z0-9]+|git-[a-z0-9-]+)-tauqeers-projects-b2ec7057\.vercel\.app)$"
METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
HEADERS = ["Accept", "Authorization", "Content-Type"]


def cors_client(origins, origin_regex=None):
    app = FastAPI()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_origin_regex=origin_regex,
        allow_credentials=True,
        allow_methods=METHODS,
        allow_headers=HEADERS,
    )
    return TestClient(app)


def preflight(client, origin):
    return client.options(
        "/api/incidents",
        headers={
            "Origin": origin,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "authorization,content-type",
        },
    )


def assert_allowed(response, origin):
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == origin
    assert response.headers["access-control-allow-credentials"] == "true"


def assert_denied(response):
    assert response.status_code == 400
    assert "access-control-allow-origin" not in response.headers


def test_production_origin_is_allowed_by_exact_allowlist():
    origin = "https://opsiq-one.vercel.app"
    assert_allowed(preflight(cors_client([origin], OPSIQ_PREVIEW_REGEX), origin), origin)


def test_opsiq_project_preview_origin_is_allowed_by_restricted_regex():
    origin = "https://opsiq-oeqhsgyw0-tauqeers-projects-b2ec7057.vercel.app"
    assert_allowed(preflight(cors_client(["https://opsiq-one.vercel.app"], OPSIQ_PREVIEW_REGEX), origin), origin)


def test_unrelated_vercel_origin_is_denied():
    response = preflight(cors_client(["https://opsiq-one.vercel.app"], OPSIQ_PREVIEW_REGEX), "https://unrelated-project.vercel.app")
    assert_denied(response)


def test_malformed_preview_origin_is_denied():
    response = preflight(cors_client(["https://opsiq-one.vercel.app"], OPSIQ_PREVIEW_REGEX), "https://opsiq--tauqeers-projects-b2ec7057.vercel.app.evil.example")
    assert_denied(response)


def test_localhost_is_allowed_only_in_development_configuration():
    origin = "http://localhost:5173"
    assert_allowed(preflight(cors_client([origin]), origin), origin)
    assert_denied(preflight(cors_client(["https://opsiq-one.vercel.app"], OPSIQ_PREVIEW_REGEX), origin))