"""
dependencies/rbac.py — Role-based access control FastAPI dependencies.

What it does:
  Provides `require_role(minimum_role)` — a dependency factory that returns
  a FastAPI Depends-compatible function. It first resolves the authenticated
  user (via get_current_user), then checks their role against the minimum
  required. Raises 403 if the role is insufficient.

Why it exists at this layer:
  Keeping RBAC logic here (not scattered in each router) means every
  protected endpoint gets consistent enforcement with a single import.

How it connects:
  - app/dependencies/auth.py supplies get_current_user
  - app/routers/sermons.py injects require_role("staff") on write endpoints
  - app/routers/sermons.py injects require_role("admin") on delete endpoints

RBAC hierarchy (lowest → highest):
  guest → member → staff → admin → superadmin
"""

from fastapi import Depends, HTTPException, status

from app.dependencies.auth import get_current_user

# Ordered lowest → highest. Index position determines rank.
_ROLE_RANK: dict[str, int] = {
    "guest":      0,
    "member":     1,
    "staff":      2,
    "admin":      3,
    "superadmin": 4,
}


def require_role(minimum: str):
    """
    Dependency factory — returns a FastAPI dependency that enforces a
    minimum role level.

    Usage:
      @router.post("/sermons")
      async def create_sermon(user=Depends(require_role("staff"))):
          ...
    """
    min_rank = _ROLE_RANK.get(minimum, 99)

    async def _check(current_user: dict = Depends(get_current_user)) -> dict:
        user_role  = current_user.get("role", "guest")
        user_rank  = _ROLE_RANK.get(user_role, 0)
        if user_rank < min_rank:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires '{minimum}' role or higher.",
            )
        return current_user

    return _check
