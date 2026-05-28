"""
crud/events.py — Database operations for public.church_events via Supabase REST.

Unlike sermons, events are fully user-managed (no sync process). All fields
in EventCreate are writable at creation time, including created_by.

How it connects:
  - app/routers/events.py calls these functions
  - app/config.py supplies supabase_url, supabase_service_key, church_id
  - tests/test_events.py patches these to avoid a live DB
"""

import uuid
from typing import Optional

import httpx

from app.config import settings
from app.schemas.event import EventCreate, EventUpdate


def _headers() -> dict:
    return {
        "apikey":        settings.supabase_service_key,
        "Authorization": f"Bearer {settings.supabase_service_key}",
        "Content-Type":  "application/json",
        "Prefer":        "return=representation",
    }


def _url() -> str:
    return f"{settings.supabase_url}/rest/v1/church_events"


# ---------------------------------------------------------------------------
# Read
# ---------------------------------------------------------------------------

def list_events(
    church_id: str | None = None,
    published_only: bool = False,
    limit: int = 50,
    offset: int = 0,
) -> list[dict]:
    """Return upcoming events for a church, ordered by start_at ascending."""
    cid = church_id or settings.church_id
    params: dict = {
        "church_id": f"eq.{cid}",
        "order":     "start_at.asc",
        "limit":     limit,
        "offset":    offset,
    }
    if published_only:
        params["is_published"] = "eq.true"

    resp = httpx.get(_url(), headers=_headers(), params=params)
    resp.raise_for_status()
    return resp.json()


def get_event(event_id: str) -> Optional[dict]:
    """Return a single event by ID, or None if not found."""
    resp = httpx.get(
        _url(),
        headers=_headers(),
        params={"id": f"eq.{event_id}", "limit": 1},
    )
    resp.raise_for_status()
    data = resp.json()
    return data[0] if data else None


# ---------------------------------------------------------------------------
# Write
# ---------------------------------------------------------------------------

def create_event(payload: EventCreate, church_id: str, created_by: str) -> dict:
    """Insert a new event row and return the created record."""
    body = payload.model_dump(exclude_none=True)
    # Serialize datetimes to ISO strings for JSON transport
    for field in ("start_at", "end_at"):
        if field in body and hasattr(body[field], "isoformat"):
            body[field] = body[field].isoformat()
    body["id"]         = str(uuid.uuid4())
    body["church_id"]  = church_id
    body["created_by"] = created_by
    resp = httpx.post(_url(), headers=_headers(), json=body)
    resp.raise_for_status()
    return resp.json()[0]


def update_event(event_id: str, payload: EventUpdate) -> dict:
    """Patch an existing event with only the fields present in payload."""
    body = payload.model_dump(exclude_unset=True, exclude_none=True)
    for field in ("start_at", "end_at"):
        if field in body and hasattr(body[field], "isoformat"):
            body[field] = body[field].isoformat()

    if not body:
        return get_event(event_id)

    resp = httpx.patch(
        _url(),
        headers=_headers(),
        params={"id": f"eq.{event_id}"},
        json=body,
    )
    resp.raise_for_status()
    return resp.json()[0]


def delete_event(event_id: str) -> None:
    """Hard-delete an event by ID."""
    resp = httpx.delete(
        _url(),
        headers=_headers(),
        params={"id": f"eq.{event_id}"},
    )
    resp.raise_for_status()
