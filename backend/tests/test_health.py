"""Phase 1 smoke tests — verifies the app boots and /api/v1/health returns 200.

Runs against FastAPI's TestClient; no network, no live DB required.
Phase 1 DoD (`03_ARCHITECTURE.md` §11): GET /api/health returns 200;
frontend renders; docker compose up works (checked separately).
"""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import create_app


def test_health_liveness_returns_200() -> None:
    app = create_app()
    client = TestClient(app)
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_route_requests_returns_explicit_unavailable_not_fake() -> None:
    """Empty 503 'no routing provider configured' — never a fabricated route list."""
    app = create_app()
    client = TestClient(app)
    response = client.post(
        "/api/v1/route-requests",
        json={
            "source": {"latitude": 12.97, "longitude": 74.88},
            "destination": {"latitude": 12.91, "longitude": 74.85},
        },
    )
    assert response.status_code == 503
    body = response.json()
    assert body["error"]["code"] == "ROUTING_PROVIDER_ERROR"


def test_openapi_schema_exports_health() -> None:
    app = create_app()
    client = TestClient(app)
    schema = client.get("/api/v1/openapi.json").json()
    assert "/api/v1/health" in schema["paths"]