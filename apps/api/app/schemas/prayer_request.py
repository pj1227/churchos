"""
schemas/prayer_request.py — Pydantic models for the prayer board.

What it does:
  Defines the three schema shapes for prayer requests:
    - PrayerRequestCreate   — inbound payload for POST /prayer-requests (public)
    - PrayerRequestRead     — outbound shape for GET responses
    - PrayerRequestModerate — inbound payload for PATCH /prayer-requests/{id}

  Field names match the DB columns exactly:
    body         — the prayer text
    name         — submitter display name (optional)
    email        — submitter contact email (optional, never exposed publicly)
    ai_reason    — AI moderation explanation
    moderated_by — UUID of the staff member who moderated

Why it exists at this layer:
  Keeps validation logic separate from route handlers and CRUD.

How it connects:
  - app/routers/prayer_requests.py uses these as request/response_model types.
  - app/crud/prayer_requests.py receives PrayerRequestCreate after validation.
"""

from typing import Literal
from pydantic import BaseModel, Field


class PrayerRequestCreate(BaseModel):
    """
    Submitted by anyone (no auth required) via the public prayer form.
    `body` is the only required field.
    """
    body:         str  = Field(..., min_length=1, max_length=2000)
    name:         str  | None = Field(None, max_length=150)
    email:        str  | None = Field(None, max_length=254)
    is_anonymous: bool = False


class PrayerRequestRead(BaseModel):
    """
    Full representation returned from GET endpoints.
    email is included so staff can see it in the moderation queue;
    the frontend should never display it on the public list.
    """
    id:           str
    church_id:    str
    name:         str | None
    email:        str | None
    body:         str
    is_anonymous: bool
    status:       str
    ai_score:     float | None
    ai_reason:    str   | None
    prayer_count: int
    submitted_at: str   | None
    moderated_at: str   | None
    moderated_by: str   | None
    is_answered:  bool
    expires_at:   str   | None
    created_at:   str   | None
    updated_at:   str   | None

    model_config = {"from_attributes": True}


class PrayerRequestPublic(BaseModel):
    """
    Safe public shape for GET /prayer-requests/public.
    email is intentionally omitted — never exposed to unauthenticated visitors.
    ai_score and ai_reason are also omitted (internal moderation data).
    moderated_by is omitted (staff UUID).
    """
    id:           str
    name:         str | None
    body:         str
    is_anonymous: bool
    status:       str
    prayer_count: int
    submitted_at: str | None
    is_answered:  bool

    model_config = {"from_attributes": True}


class PrayerRequestModerate(BaseModel):
    """
    Sent by staff via PATCH /prayer-requests/{id} to approve or reject.
    `reason` populates ai_reason in the DB when staff overrides the AI decision.
    """
    status: Literal["approved", "rejected"]
    reason: str | None = None
