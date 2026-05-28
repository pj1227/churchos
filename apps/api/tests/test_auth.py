"""
test_auth.py — TDD tests for JWT authentication.

These tests are written BEFORE any auth implementation exists.
They will fail with either 404 (route missing) or ModuleNotFoundError
(dependency not yet created). That is the expected TDD state.

What we are testing:
  GET /me — returns the authenticated user's profile.

Failure modes this covers:
  1. No Authorization header         → 401
  2. Malformed token (not a JWT)     → 401
  3. Token signed with wrong secret  → 401
  4. Expired token                   → 401
  5. Token without 'Bearer ' prefix  → 401
  6. Valid token + profile in DB     → 200 + profile fields
  7. Valid token + no profile in DB  → 404

How it connects:
  - Uses PyJWT (already in requirements.txt) to mint test JWTs.
  - Mocks `app.dependencies.auth.get_profile` so tests never hit the DB.
  - The `client` fixture comes from conftest.py.

JWT secret:
  The real secret is SUPABASE_JWT_SECRET in the environment.
  Tests use TEST_JWT_SECRET — a hardcoded dummy — so CI never needs
  real credentials to run the auth test suite.
"""
import time
from unittest.mock import patch

from fastapi.testclient import TestClient
import jwt


# ---------------------------------------------------------------------------
# Test constants — never use real credentials here
# ---------------------------------------------------------------------------
TEST_JWT_SECRET = "test-jwt-secret-for-pytest-only-32chars!!"
TEST_USER_ID = "550e8400-e29b-41d4-a716-446655440000"
TEST_EMAIL = "test@libbynaz.org"

MOCK_PROFILE = {
    "id": TEST_USER_ID,
    "email": TEST_EMAIL,
    "display_name": None,
    "role": "member",
    "church_slug": "libby-naz",
}


# ---------------------------------------------------------------------------
# Helper — mint a Supabase-shaped HS256 JWT for testing
# ---------------------------------------------------------------------------
def make_token(
    sub: str = TEST_USER_ID,
    email: str = TEST_EMAIL,
    secret: str = TEST_JWT_SECRET,
    expires_in: int = 3600,
) -> str:
    """
    Create a signed JWT that mirrors the shape of a Supabase access token.

    The `role` claim is always 'authenticated' — that is what Supabase sets.
    Our app role ('member', 'admin', etc.) lives in public.profiles, not
    the token itself.
    """
    now = int(time.time())
    payload = {
        "sub": sub,
        "email": email,
        "role": "authenticated",  # Supabase's claim, not our RBAC role
        "iat": now,
        "exp": now + expires_in,
    }
    return jwt.encode(payload, secret, algorithm="HS256")


# ---------------------------------------------------------------------------
# /me — unauthenticated cases (all must return 401)
# ---------------------------------------------------------------------------
class TestMeUnauthenticated:
    """
    Every case here represents a request that must be rejected.
    The implementation must return 401, not 403, 404, or 500.
    """

    def test_no_auth_header_returns_401(self, client: TestClient):
        """Missing Authorization header entirely → 401."""
        response = client.get("/me")
        assert response.status_code == 401

    def test_malformed_token_returns_401(self, client: TestClient):
        """Garbage string in Bearer position → 401."""
        response = client.get(
            "/me", headers={"Authorization": "Bearer not.a.real.jwt"}
        )
        assert response.status_code == 401

    def test_wrong_secret_returns_401(self, client: TestClient):
        """
        Token signed with the wrong secret → 401.
        Ensures signature verification is actually happening.
        """
        token = make_token(secret="completely-wrong-secret-abc123456789")
        response = client.get("/me", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 401

    def test_expired_token_returns_401(self, client: TestClient):
        """
        Token with exp in the past → 401.
        expires_in=-1 sets exp to one second ago.
        """
        token = make_token(expires_in=-1)
        response = client.get("/me", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 401

    def test_missing_bearer_prefix_returns_401(self, client: TestClient):
        """
        Raw token without 'Bearer ' prefix → 401.
        The Authorization header format must be 'Bearer <token>'.
        """
        token = make_token()
        response = client.get("/me", headers={"Authorization": token})
        assert response.status_code == 401


# ---------------------------------------------------------------------------
# /me — authenticated cases
# ---------------------------------------------------------------------------
class TestMeAuthenticated:
    """
    Valid token cases. These mock get_profile so no DB is needed.

    The patch target 'app.dependencies.auth.get_profile' must match the
    actual import path once the dependency module is created.
    """

    def test_valid_token_returns_200_with_profile(self, client: TestClient):
        """
        Valid JWT + matching profile row → 200 with all profile fields.
        The response must include id, email, role, and church_slug.
        """
        token = make_token()

        with patch(
            "app.dependencies.auth.get_profile",
            return_value=MOCK_PROFILE,
        ):
            response = client.get(
                "/me", headers={"Authorization": f"Bearer {token}"}
            )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == TEST_USER_ID
        assert data["email"] == TEST_EMAIL
        assert data["role"] == "member"
        assert data["church_slug"] == "libby-naz"

    def test_valid_token_no_profile_returns_404(self, client: TestClient):
        """
        Valid JWT but no matching row in public.profiles → 404.
        This happens when a Supabase user exists but the trigger failed
        or the profile was deleted manually.
        """
        token = make_token()

        with patch(
            "app.dependencies.auth.get_profile",
            return_value=None,
        ):
            response = client.get(
                "/me", headers={"Authorization": f"Bearer {token}"}
            )

        assert response.status_code == 404
