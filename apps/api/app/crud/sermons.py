"""
crud/sermons.py — Database operations for public.sermons via Supabase REST.

What it does:
  Plain functions (not FastAPI dependencies) for querying and mutating the
  sermons table. All functions are patchable in tests so no live DB is needed.

Key design decisions:
  - Sermons are primarily Logos-synced; the admin only edits a subset of fields
  - list_sermons filters by church_id (not church_slug) to match the FK schema
  - create_sermon generates a uuid4 string ID for manually created sermons
  - update_sermon accepts only human-editable fields (SermonUpdate PATCH model)

How it connects:
  - app/routers/sermons.py calls these functions
  - app/config.py supplies supabase_url, supabase_service_key, church_id
  - tests/test_sermons.py patches these to avoid a live DB
"""

import uuid
from typing import Optional

import httpx

from app.config import settings
from app.schemas.sermon import SermonCreate, SermonUpdate


def _headers() -> dict:
    return {
        "apikey":        settings.supabase_service_key,
        "Authorization": f"Bearer {settings.supabase_service_key}",
        "Content-Type":  "application/json",
        "Prefer":        "return=representation",
    }


def _url() -> str:
    return f"{settings.supabase_url}/rest/v1/sermons"


# ---------------------------------------------------------------------------
# Read
# ---------------------------------------------------------------------------

def list_sermons(
    church_id: str | None = None,
    published_only: bool = False,
    limit: int = 50,
    offset: int = 0,
) -> list[dict]:
    """
    Return a paginated list of sermons for a church, newest first.

    church_id defaults to settings.church_id if not provided.
    published_only=True filters to is_published=true rows only.
    """
    cid = church_id or settings.church_id
    params: dict = {
        "church_id": f"eq.{cid}",
        "order":     "date.desc",
        "limit":     limit,
        "offset":    offset,
    }
    if published_only:
        params["is_published"] = "eq.true"

    resp = httpx.get(_url(), headers=_headers(), params=params)
    resp.raise_for_status()
    return resp.json()


def get_sermon(sermon_id: str) -> Optional[dict]:
    """Return a single sermon by ID, or None if not found."""
    resp = httpx.get(
        _url(),
        headers=_headers(),
        params={"id": f"eq.{sermon_id}", "limit": 1},
    )
    resp.raise_for_status()
    data = resp.json()
    return data[0] if data else None


# ---------------------------------------------------------------------------
# Write
# ---------------------------------------------------------------------------

def create_sermon(payload: SermonCreate, church_id: str) -> dict:
    """
    Insert a manually created sermon (not from Logos sync).
    Generates a uuid4 string ID to match the varchar(36) PK convention.
    """
    body = payload.model_dump(exclude_none=True)
    body["id"]         = str(uuid.uuid4())
    body["church_id"]  = church_id
    resp = httpx.post(_url(), headers=_headers(), json=body)
    resp.raise_for_status()
    return resp.json()[0]


def update_sermon(sermon_id: str, payload: SermonUpdate) -> dict:
    """
    Patch human-editable fields on an existing sermon.
    Logos-sync fields are excluded from this operation.
    """
    body = payload.model_dump(exclude_unset=True, exclude_none=True)
    if not body:
        # Nothing to update — fetch and return current state
        return get_sermon(sermon_id)

    resp = httpx.patch(
        _url(),
        headers=_headers(),
        params={"id": f"eq.{sermon_id}"},
        json=body,
    )
    resp.raise_for_status()
    return resp.json()[0]


def delete_sermon(sermon_id: str) -> None:
    """Hard-delete a sermon by ID."""
    resp = httpx.delete(
        _url(),
        headers=_headers(),
        params={"id": f"eq.{sermon_id}"},
    )
    resp.raise_for_status()
