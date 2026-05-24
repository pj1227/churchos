"""
app/dependencies/auth.py — FastAPI dependency for JWT verification.

What it does:
  Extracts the Bearer token from the Authorization header and verifies
  it against SUPABASE_JWT_SECRET. Raises HTTP 401 on any failure.

Why it exists at this layer:
  FastAPI's dependency injection system lets us declare `verify_jwt` as
  a parameter on any route. FastAPI calls it automatically before the
  route handler runs — the handler only executes if the token is valid.
  Centralising auth here means we never forget to protect a route.

How it connects:
  - Injected into app/routers/auth.py (/auth/me) and every future
    protected endpoint.
  - Reads SUPABASE_JWT_SECRET from environment (set in .env / CI secrets).
  - In tests, SUPABASE_JWT_SECRET is set to a known value so we can
    mint valid tokens without hitting Supabase.
"""

import os
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

_bearer = HTTPBearer(auto_error=False)

JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET", "")
JWT_ALGORITHM = "HS256"


def verify_jwt(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
) -> dict:
    """
    Verify the Bearer JWT and return its decoded payload.

    Raises 401 if:
      - Authorization header is absent or not Bearer scheme
      - Token signature is invalid
      - Token is expired
      - JWT_SECRET is not configured
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not JWT_SECRET:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Auth not configured on this server",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = jwt.decode(
            credentials.credentials,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM],
        )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
