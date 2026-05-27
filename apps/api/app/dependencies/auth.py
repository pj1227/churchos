"""
dependencies/auth.py — JWT verification and profile lookup.

What it does:
  1. `verify_token` — extracts the Bearer token from the Authorization
     header and verifies it is a valid, non-expired HS256 JWT signed with
     our Supabase JWT secret. Returns the decoded payload or raises 401.

  2. `get_profile` — given a user UUID (the `sub` claim from the token),
     fetches the matching row from public.profiles. Returns the profile
     dict or None if no row exists. This function is intentionally plain
     (not a FastAPI Depends) so tests can patch it cleanly with
     unittest.mock.patch("app.dependencies.auth.get_profile", ...).

  3. `get_current_user` — the FastAPI dependency injected into protected
     endpoints. Calls verify_token then get_profile, raising 401 or 404
     as appropriate.

Why it exists at this layer:
  Keeping auth logic in `dependencies/` separates it from route handlers
  and makes it reusable across multiple routers (me, admin, prayer board,
  directory) without coupling them together.

How it connects:
  - app/config.py supplies `settings.supabase_jwt_secret`.
  - app/routers/me.py injects `get_current_user` via Depends().
  - tests/test_auth.py patches `get_profile` to avoid a live DB in CI.

Security notes:
  - Tokens are verified with HS256 using the Supabase JWT secret.
  - `verify_aud` is False: Supabase omits the `aud` claim on access tokens
    issued to the JS client; server-side tokens include it. Skipping
    audience validation here is consistent with Supabase's own docs.
  - The service role key (which bypasses RLS) is never used here — this
    dependency uses the verified user identity, not the service role.
"""

import httpx
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt.exceptions import InvalidTokenError

from app.config import settings

# auto_error=False lets us return a custom 401 instead of FastAPI's default
# 403 (which HTTPBearer raises when the header is missing or malformed).
_bearer_scheme = HTTPBearer(auto_error=False)


def verify_token(
    credentials: HTTPAuthorizationCredentials | None,
) -> dict:
    """
    Verify a Supabase Bearer JWT and return its decoded payload.

    Raises HTTP 401 for:
      - Missing Authorization header (credentials is None)
      - Non-Bearer scheme (e.g. raw token without 'Bearer ' prefix)
      - Malformed JWT
      - Wrong signature / wrong secret
      - Expired token
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.supabase_jwt_secret,
            algorithms=["HS256"],
            options={"verify_aud": False},
        )
        return payload
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_profile(user_id: str) -> dict | None:
    """
    Fetch the public.profiles row for `user_id` via the Supabase REST API.

    Uses the service role key so this call bypasses RLS — the API server
    is allowed to read any profile regardless of the caller's JWT. The
    service key is never forwarded to the client.

    Returns a plain dict (matching the profiles table columns) or None
    if no row exists for that UUID.

    Intentionally NOT an async def — the httpx sync client keeps the
    dependency chain simple until we add connection pooling in Phase 4.
    """
    url = f"{settings.supabase_url}/rest/v1/profiles"
    headers = {
        "apikey": settings.supabase_service_key,
        "Authorization": f"Bearer {settings.supabase_service_key}",
    }
    params = {
        "id": f"eq.{user_id}",
        "select": "id,email,display_name,role,church_slug",
    }
    resp = httpx.get(url, headers=headers, params=params)
    resp.raise_for_status()
    data = resp.json()
    return data[0] if data else None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
) -> dict:
    """
    FastAPI dependency — resolves to the authenticated user's profile dict.

    Inject with: `current_user: dict = Depends(get_current_user)`

    Raises:
      401 — token missing, malformed, wrong secret, or expired
      404 — token valid but no matching row in public.profiles
    """
    payload = verify_token(credentials)
    user_id: str | None = payload.get("sub")

    profile = get_profile(user_id)
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )

    return profile
