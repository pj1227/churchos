"""
routers/me.py — Authenticated user profile endpoint.

What it does:
  Exposes GET /me, which returns the authenticated user's profile from
  public.profiles. This is the primary endpoint clients call after login
  to get the user's role, display name, and church context.

Why it exists at this layer:
  Keeping route handlers thin (just Depends + return) and pushing logic
  into dependencies/auth.py means this file only needs to change if the
  response shape or URL changes.

How it connects:
  - `get_current_user` (from dependencies/auth.py) handles all auth logic:
    token extraction, JWT verification, and profile lookup.
  - app/main.py registers this router with `app.include_router(router)`.
  - tests/test_auth.py exercises this endpoint end-to-end.

Response shape:
  {
    "id":           "<uuid>",
    "email":        "user@example.com",
    "display_name": null | "Alice",
    "role":         "member" | "staff" | "admin" | "superadmin",
    "church_slug":  "libby-naz"
  }
"""

from fastapi import APIRouter, Depends

from app.dependencies.auth import get_current_user

router = APIRouter(tags=["auth"])


@router.get("/me")
async def me(current_user: dict = Depends(get_current_user)) -> dict:
    """
    Return the authenticated user's profile.

    Requires a valid Supabase access token in the Authorization header:
      Authorization: Bearer <token>

    Returns the public.profiles row for the authenticated user.
    """
    return current_user
