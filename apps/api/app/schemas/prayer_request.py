"""
schemas/prayer_request.py — Pydantic models for the prayer board.

What it does:
  Defines the three schema shapes for prayer requests:
    - PrayerRequestCreate  — inbound payload for POST /prayer-requests (public)
    - PrayerRequestRead    — outbound shape for GET responses
    - PrayerRequestModerate — inbound payload for PATCH /prayer-requests/{id}

Why it exists at this layer:
  Keeps validation logic (field types, constraints, optional vs required)
  separate from route handlers and CRUD functions. Pydantic validates at
  the FastAPI boundary so malformed requests are rejected before they reach
  any business logic.

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
    is_anonymous: bool = False


class PrayerRequestRead(BaseModel):
    """
    Full representation returned from GET endpoints.
    Includes moderation metadata so staff can see AI scores in the queue.
    """
    id:           str
    church_id:    str
    name:         str | None
    body:         str
    is_anonymous: bool
    status:       str
    ai_score:     float | None
    ai_reason:    str   | None
    submitted_at: str
    moderated_at: str   | None
    moderated_by: str   | None
    is_answered:  bool
    created_at:   str
    updated_at:   str

    model_config = {"from_attributes": True}


class PrayerRequestModerate(BaseModel):
    """
    Sent by staff via PATCH /prayer-requests/{id} to approve or reject.
    `reason` is optional but recommended when rejecting.
    """
    status: Literal["approved", "rejected"]
    reason: str | None = None
