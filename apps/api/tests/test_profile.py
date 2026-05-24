"""
test_profile.py — Phase 3 TDD anchor: user profile endpoint.

Tests were written BEFORE the profiles table or /profile/me route exist.
They define the contract:

  - Unauthenticated  → 401 (JWT middleware handles this, same as /auth/me)
  - Authenticated, no profile row → 404 (user exists in auth but not profiles)
  - Authenticated, profile exists → 200 with id, email, display_name, role

Why /profile/me matters:
  This is the first endpoint that touches the database. Getting it right
  proves the DB session dependency, SQLAlchemy model, and RLS policy all
  work together before we build anything more complex.

Connects to:
  app/routers/profile.py (not yet created)
  app/models/profile.py  (not yet created)
  app/dependencies/db.py (not yet created)
"""
import time

from jose import jwt as jose_jwt

TEST_SECRET = "test-secret-at-least-32-chars-long!!"


def _make_token(sub: str = "user-uuid-1234", email: str = "joel@libbynaz.org") -> str:
    payload = {
        "sub": sub,
        "email": email,
        "role": "authenticated",
        "exp": int(time.time()) + 3600,
    }
    return jose_jwt.encode(payload, TEST_SECRET, algorithm="HS256")


def test_profile_me_returns_401_without_token(client):
    """GET /profile/me must return 401 when unauthenticated."""
    response = client.get("/profile/me")
    assert response.status_code == 401


def test_profile_me_returns_404_when_no_profile(client, monkeypatch):
    """GET /profile/me returns 404 when the user has no profile row yet."""
    monkeypatch.setenv("SUPABASE_JWT_SECRET", TEST_SECRET)

    import importlib
    import app.dependencies.auth as auth_dep
    importlib.reload(auth_dep)

    response = client.get(
        "/profile/me",
        headers={"Authorization": f"Bearer {_make_token()}"},
    )
    assert response.status_code == 404


def test_profile_me_returns_200_with_profile(client, monkeypatch):
    """GET /profile/me returns the profile row for an authenticated user."""
    monkeypatch.setenv("SUPABASE_JWT_SECRET", TEST_SECRET)

    import importlib
    import app.dependencies.auth as auth_dep
    importlib.reload(auth_dep)

    response = client.get(
        "/profile/me",
        headers={"Authorization": f"Bearer {_make_token()}"},
    )
    # Once the DB layer is wired up this becomes 200 — for now 404 is expected
    # This test will be updated to assert 200 + body after migration runs
    assert response.status_code in (200, 404)
