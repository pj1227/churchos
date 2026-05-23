"""
test_health.py — Phase 0 TDD anchor.

This test was written BEFORE the /health route existed in main.py.
It defines the contract: any future change to the health endpoint must
satisfy these assertions or update them deliberately.

Connects to: app/main.py (the FastAPI app) via conftest.py client fixture.
"""


def test_health_returns_200(client):
    """GET /health must return HTTP 200."""
    response = client.get("/health")
    assert response.status_code == 200


def test_health_returns_status_ok(client):
    """Response body must include status: ok."""
    response = client.get("/health")
    data = response.json()
    assert data["status"] == "ok"


def test_health_returns_version(client):
    """Response body must include the current semantic version."""
    response = client.get("/health")
    data = response.json()
    assert data["version"] == "0.1.0"


def test_health_returns_codename(client):
    """Response body must include the release codename."""
    response = client.get("/health")
    data = response.json()
    assert data["codename"] == "Kootenai"
