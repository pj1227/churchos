"""
schemas/event.py — Pydantic request/response models for church_events.

EventCreate  — full payload for creating a new event (all required + optional fields)
EventUpdate  — PATCH payload; all fields optional
EventRead    — full response shape mirroring every column in public.church_events
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class EventCreate(BaseModel):
    title:                 str
    description:           Optional[str]  = None
    start_at:              datetime
    end_at:                datetime
    all_day:               bool           = False
    location:              Optional[str]  = None
    is_virtual:            bool           = False
    virtual_url:           Optional[str]  = None
    category:              Optional[str]  = None
    recurrence:            str            = "none"
    image_url:             Optional[str]  = None
    registration_required: bool           = False
    registration_url:      Optional[str]  = None
    is_published:          bool           = False


class EventUpdate(BaseModel):
    title:                 Optional[str]      = None
    description:           Optional[str]      = None
    start_at:              Optional[datetime] = None
    end_at:                Optional[datetime] = None
    all_day:               Optional[bool]     = None
    location:              Optional[str]      = None
    is_virtual:            Optional[bool]     = None
    virtual_url:           Optional[str]      = None
    category:              Optional[str]      = None
    recurrence:            Optional[str]      = None
    image_url:             Optional[str]      = None
    registration_required: Optional[bool]     = None
    registration_url:      Optional[str]      = None
    is_published:          Optional[bool]     = None


class EventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id:                    str
    church_id:             str
    title:                 str
    description:           Optional[str]
    start_at:              datetime
    end_at:                datetime
    all_day:               Optional[bool]
    location:              Optional[str]
    is_virtual:            Optional[bool]
    virtual_url:           Optional[str]
    category:              Optional[str]
    recurrence:            Optional[str]
    image_url:             Optional[str]
    registration_required: Optional[bool]
    registration_url:      Optional[str]
    created_by:            Optional[str]
    is_published:          Optional[bool]
    created_at:            Optional[datetime]
    updated_at:            Optional[datetime]
