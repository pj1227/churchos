"""
app/routers/auth.py — Authentication routes.

What it does:
  Exposes /auth/me — a protected endpoint that returns the caller's
  identity from their JWT payload. No database hit required; the token
  itself is the source of truth for identity at this layer.

Why it exists at this layer:
  Separating auth routes into their own router keeps main.py clean and
  makes it easy to version or prefix the auth surface independently.

How it connects:
  - Registered on the FastAPI app in app/main.py with prefix /auth.
  - Uses verify_jwt from app/dependencies/auth.py — any route that
    lists it as a dependency is automatically protected.
"""

from typing import Annotated

from fastapi import APIRouter, Depends

from app.dependencies.auth import verify_jwt

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/me")
async def get_me(payload: Annotated[dict, Depends(verify_jwt)]) -> dict:
    """
    Return the authenticated user's identity from their JWT payload.

    The JWT contains the Supabase user id (sub), email, and role.
    We return only what the client needs — never the raw token.
    """
    return {
        "id": payload.get("sub"),
        "email": payload.get("email"),
        "role": payload.get("role", "authenticated"),
    }
