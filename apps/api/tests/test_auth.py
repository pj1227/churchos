"""
test_auth.py — Phase 3 TDD anchor: JWT authentication.

These tests were written BEFORE any auth implementation exists.
They define the contract for the /auth/me endpoint:

  - No token       → 401 Unauthorized
  - Bad token      → 401 Unauthorized
  - Malformed header → 401 Unauthorized

Why /auth/me first:
  It's the simplest possible protected endpoint — no DB, no side effects.
  Getting it right proves the JWT middleware works before we wire up
  anything else. Every other protected endpoint in the API will depend
  on the same verify_jwt dependency we build here.

Connects to: app/routers/auth.py (not yet created) via conftest.py client.
"""


def test_me_returns_401_without_token(client):
    """GET /auth/me must return 401 when no Authorization header is present."""
    response = client.get("/auth/me")
    assert response.status_code == 401


def test_me_returns_401_with_invalid_token(client):
    """GET /auth/me must return 401 when the Bearer token is forged or expired."""
    response = client.get(
        "/auth/me",
        headers={"Authorization": "Bearer this.is.not.a.real.jwt"},
    )
    assert response.status_code == 401


def test_me_returns_401_with_malformed_header(client):
    """GET /auth/me must return 401 when Authorization header format is wrong."""
    response = client.get(
        "/auth/me",
        headers={"Authorization": "Token abc123"},
    )
    assert response.status_code == 401
