"""
app/routers/profile.py — User profile routes.

What it does:
  Exposes /profile/me — returns the authenticated user's profile row
  from the public.profiles table. Returns 404 if no profile exists yet
  (e.g. user just signed up and the trigger hasn't run, or in tests).

Why it exists at this layer:
  Separating profile routes from auth routes keeps concerns clear:
  auth/ handles token operations, profile/ handles user data. Both
  share the same verify_jwt dependency for protection.

How it connects:
  - Registered on the FastAPI app in app/main.py with prefix /profile.
  - verify_jwt from app/dependencies/auth.py provides the decoded payload.
  - DB session from app/dependencies/db.py (Phase 3, wired up after Alembic).
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies.auth import verify_jwt

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("/me")
async def get_profile_me(
    payload: Annotated[dict, Depends(verify_jwt)],
) -> dict:
    """
    Return the authenticated user's profile.

    Currently returns 404 — the DB session dependency and SQLAlchemy
    query will be added once the Alembic migration creates the profiles
    table. The endpoint shape and auth contract are established here.
    """
    # TODO(phase-3): query public.profiles where id = payload["sub"]
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Profile not found",
    )
