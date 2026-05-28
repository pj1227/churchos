"""
schemas/sermon.py — Pydantic request/response models for sermons.

What it does:
  SermonRead    — full response shape, mirrors every column in public.sermons
  SermonCreate  — payload for manually creating a sermon (non-Logos churches)
  SermonUpdate  — PATCH payload; all fields optional so callers send only diffs

Why separate Create vs Update:
  Logos-synced fields (logos_id, logos_url, etc.) are never accepted from the
  admin form — they're set by the sync process. SermonCreate/Update only expose
  the human-editable columns.

How it connects:
  - app/routers/sermons.py uses these as FastAPI type annotations
  - app/crud/sermons.py receives these on write operations
  - Tests import MOCK_SERMON shaped like SermonRead
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class SermonCreate(BaseModel):
    """
    Payload for manually creating a sermon.
    Used by churches that don't sync from Logos.
    All Logos-specific fields are absent — those come from the sync process only.
    """
    title:               str
    speaker_name:        str = ""
    series:              Optional[str] = None
    date:                str           # "YYYY-MM-DD" — stored as varchar(10)
    description:         Optional[str] = None
    notes:               Optional[str] = None
    scripture_reference: Optional[str] = None
    thumbnail_url:       Optional[str] = None
    tags:                Optional[str] = None
    is_published:        bool = True


class SermonUpdate(BaseModel):
    """
    PATCH payload — every field is optional.
    Only human-editable columns; Logos fields are read-only via the sync.
    """
    title:               Optional[str]  = None
    speaker_name:        Optional[str]  = None
    series:              Optional[str]  = None
    date:                Optional[str]  = None
    description:         Optional[str]  = None
    notes:               Optional[str]  = None
    scripture_reference: Optional[str]  = None
    thumbnail_url:       Optional[str]  = None
    tags:                Optional[str]  = None
    is_published:        Optional[bool] = None


class SermonRead(BaseModel):
    """Full response shape — mirrors every column in public.sermons."""
    model_config = ConfigDict(from_attributes=True)

    id:                    str
    church_id:             str
    logos_id:              Optional[str]
    logos_url:             Optional[str]
    logos_embed_url:       Optional[str]
    logos_series_id:       Optional[str]
    title:                 str
    speaker_name:          Optional[str]
    series:                Optional[str]
    date:                  str
    description:           Optional[str]
    notes:                 Optional[str]
    scripture_reference:   Optional[str]
    thumbnail_url:         Optional[str]
    series_thumbnail_url:  Optional[str]
    duration_seconds:      Optional[int]
    tags:                  Optional[str]
    has_audio:             Optional[bool]
    has_video:             Optional[bool]
    has_slides:            Optional[bool]
    is_published:          Optional[bool]
    logos_published_at:    Optional[datetime]
    logos_updated_at:      Optional[datetime]
    first_synced_at:       Optional[datetime]
    last_synced_at:        Optional[datetime]
    created_at:            Optional[datetime]
    updated_at:            Optional[datetime]
