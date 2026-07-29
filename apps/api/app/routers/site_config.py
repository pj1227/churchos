"""
routers/site_config.py — Site configuration API endpoints.

Endpoint summary:
  GET  /site-config         staff+  — list all config keys; secrets masked
  GET  /site-config/public  none    — CMS content keys only (is_public=true)
  GET  /site-config/{key}   staff+  — get a single key; secret masked
  PUT  /site-config/{key}   admin+  — upsert a key/value pair

Security:
  - All endpoints require staff role minimum (read), except /public
  - Only admin+ can write config values
  - is_secret=true values are returned as "***" — the raw value is never
    sent to the client. Internal code uses crud.site_config.get_raw_value().
  - /public is filtered at the crud layer (is_public AND NOT is_secret) —
    the only site_config data ever exposed without auth. Used by apps/web's
    useSiteContent() composable for church name/address/contact/page copy.

Route ordering note:
  GET /public is declared before GET /{key} so it isn't captured by the
  {key} path parameter (FastAPI matches routes in declaration order).

How it connects:
  - app/main.py registers this router with prefix="/site-config"
  - app/crud/site_config.py handles all Supabase calls
  - app/schemas/site_config.py defines request/response shapes
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status

from app.crud import site_config as config_crud
from app.crud import storage as storage_crud
from app.dependencies.rbac import require_role
from app.schemas.site_config import SiteConfigRead, SiteConfigWrite

router = APIRouter(prefix="/site-config", tags=["config"])

_MASK = "***"

_LOGO_EXTENSIONS = {
    "svg":  "image/svg+xml",
    "png":  "image/png",
    "jpg":  "image/jpeg",
    "jpeg": "image/jpeg",
    "gif":  "image/gif",
}
_LOGO_MAX_BYTES = 2 * 1024 * 1024  # 2MB


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


@router.get("/public")
async def list_public_site_config() -> dict:
    """
    Public CMS content read — no auth. Returns a flat {key: value} map of
    every is_public=true, non-secret config row (church name, address,
    contact info, page copy, etc.) for use by the public website.
    """
    rows = config_crud.list_public_config()
    return {row["key"]: row["value"] for row in rows}


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


@router.post("/logo")
async def upload_logo(
    file: UploadFile,
    current_user: dict = Depends(require_role("staff")),
) -> dict:
    """
    Upload a church logo image. Validates extension and size, uploads to
    Supabase Storage, and writes the resulting URL to the church_logo_url
    config key (is_public=true) so the public site can render it.
    """
    ext = (file.filename or "").rsplit(".", 1)[-1].lower() if "." in (file.filename or "") else ""
    if ext not in _LOGO_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type '.{ext}'. Allowed: {', '.join(sorted(_LOGO_EXTENSIONS))}.",
        )

    content = await file.read()
    if len(content) > _LOGO_MAX_BYTES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size is {_LOGO_MAX_BYTES // (1024 * 1024)}MB.",
        )

    path = f"logo-{uuid.uuid4().hex}.{ext}"
    url = storage_crud.upload_public_file(
        storage_crud.LOGO_BUCKET, path, content, _LOGO_EXTENSIONS[ext],
    )
    config_crud.set_config_value(
        "church_logo_url",
        SiteConfigWrite(value=url, is_public=True),
    )
    return {"url": url}
