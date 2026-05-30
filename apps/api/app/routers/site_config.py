"""
routers/site_config.py — Site configuration API endpoints.

Endpoint summary:
  GET  /site-config        staff+   — list all config keys; secrets masked
  GET  /site-config/{key}  staff+   — get a single key; secret masked
  PUT  /site-config/{key}  admin+   — upsert a key/value pair

Security:
  - All endpoints require staff role minimum (read)
  - Only admin+ can write config values
  - is_secret=true values are returned as "***" — the raw value is never
    sent to the client. Internal code uses crud.site_config.get_raw_value().

How it connects:
  - app/main.py registers this router with prefix="/site-config"
  - app/crud/site_config.py handles all Supabase calls
  - app/schemas/site_config.py defines request/response shapes
"""

from fastapi import APIRouter, Depends, HTTPException, status

from app.crud import site_config as config_crud
from app.dependencies.rbac import require_role
from app.schemas.site_config import SiteConfigRead, SiteConfigWrite

router = APIRouter(prefix="/site-config", tags=["config"])

_MASK = "***"


def _mask(row: dict) -> dict:
    """Replace value with '***' for secret config rows."""
    if row.get("is_secret") and row.get("value") is not None:
        return {**row, "value": _MASK}
    return row


@router.get("", response_model=list[SiteConfigRead])
async def list_site_config(
    current_user: dict = Depends(require_role("staff")),
) -> list[dict]:
    """List all config keys for this deployment. Secret values are masked."""
    rows = config_crud.list_config()
    return [_mask(r) for r in rows]


@router.get("/{key}", response_model=SiteConfigRead)
async def get_site_config(
    key: str,
    current_user: dict = Depends(require_role("staff")),
) -> dict:
    """Fetch a single config value by key. Secret values are masked."""
    row = config_crud.get_config_value(key)
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Config key '{key}' not found",
        )
    return _mask(row)


@router.put("/{key}", response_model=SiteConfigRead)
async def set_site_config(
    key: str,
    payload: SiteConfigWrite,
    current_user: dict = Depends(require_role("admin")),
) -> dict:
    """
    Upsert a config key/value pair. Admin+ required.
    Creates the row if it doesn't exist; updates if it does.
    """
    row = config_crud.set_config_value(key, payload)
    return _mask(row)
