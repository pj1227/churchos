"""
crud/site_config.py — Supabase REST calls for site_config table.

What it does:
  list_config      — fetch all config rows for the church
  get_config_value — fetch a single row by key
  set_config_value — upsert a key/value pair (INSERT ... ON CONFLICT UPDATE)
  get_raw_value    — fetch the raw (unmasked) value for internal use only
                     (e.g. to read prayer_chain_email before sending email)

Why it exists at this layer:
  Isolating DB calls here keeps routers thin and makes every call
  independently patchable in tests.

Security note:
  Masking of is_secret values happens in the router, not here.
  get_raw_value bypasses masking — only call from server-side logic,
  never return its output directly to the client.
"""

from datetime import datetime, timezone

import httpx

from app.config import settings
from app.schemas.site_config import SiteConfigWrite


def _headers() -> dict:
    return {
        "apikey":        settings.supabase_service_key,
        "Authorization": f"Bearer {settings.supabase_service_key}",
        "Content-Type":  "application/json",
        "Prefer":        "return=representation",
    }


def _base_url() -> str:
    return f"{settings.supabase_url}/rest/v1/site_config"


def list_config(church_id: str = "") -> list[dict]:
    """Fetch all config rows for the church."""
    cid = church_id or settings.church_id
    if not cid:
        return []
    params = {"church_id": f"eq.{cid}", "order": "key.asc", "select": "*"}
    resp = httpx.get(_base_url(), headers=_headers(), params=params)
    resp.raise_for_status()
    return resp.json()


def get_config_value(key: str, church_id: str = "") -> dict | None:
    """Fetch a single config row by key. Returns None if not found."""
    cid = church_id or settings.church_id
    if not cid:
        return None
    params = {"church_id": f"eq.{cid}", "key": f"eq.{key}", "select": "*"}
    resp = httpx.get(_base_url(), headers=_headers(), params=params)
    resp.raise_for_status()
    data = resp.json()
    return data[0] if data else None


def get_raw_value(key: str, church_id: str = "") -> str | None:
    """
    Fetch the unmasked string value for a config key.
    For internal server-side use only — never expose to clients.
    Returns None if key not found.
    """
    row = get_config_value(key, church_id)
    return row["value"] if row else None


def set_config_value(key: str, payload: SiteConfigWrite, church_id: str = "") -> dict:
    """
    Upsert a config key/value pair using ON CONFLICT (church_id, key) DO UPDATE.
    Creates the row if it doesn't exist; updates if it does.
    """
    cid = church_id or settings.church_id
    now = datetime.now(timezone.utc).isoformat()
    row = {
        "church_id":  cid,
        "key":        key,
        "value":      payload.value,
        "is_secret":  payload.is_secret,
        "is_json":    payload.is_json,
        "updated_at": now,
    }
    # Supabase upsert: Prefer: resolution=merge-duplicates
    headers = {**_headers(), "Prefer": "return=representation,resolution=merge-duplicates"}
    resp = httpx.post(_base_url(), json=row, headers=headers)
    resp.raise_for_status()
    data = resp.json()
    return data[0] if isinstance(data, list) else data
