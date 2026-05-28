"""
models/event.py — SQLAlchemy ORM model for public.church_events.

Mirrors the existing Supabase table exactly. Events are manually created
by staff/admin via the admin dashboard (unlike sermons which are Logos-synced).

How it connects:
  - app/models/base.py supplies DeclarativeBase
  - app/crud/events.py queries this model
  - alembic/env.py imports Base.metadata for migration autogeneration
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class ChurchEvent(Base):
    __tablename__ = "church_events"

    id:                    Mapped[str]            = mapped_column(String(36),  primary_key=True)
    church_id:             Mapped[str]            = mapped_column(String(36),  ForeignKey("churches.id", ondelete="CASCADE"), nullable=False, index=True)
    title:                 Mapped[str]            = mapped_column(String(300), nullable=False)
    description:           Mapped[Optional[str]]  = mapped_column(Text,        nullable=True)
    start_at:              Mapped[datetime]       = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    end_at:                Mapped[datetime]       = mapped_column(DateTime(timezone=True), nullable=False)
    all_day:               Mapped[Optional[bool]] = mapped_column(Boolean,     nullable=True, default=False)
    location:              Mapped[Optional[str]]  = mapped_column(String(300), nullable=True)
    is_virtual:            Mapped[Optional[bool]] = mapped_column(Boolean,     nullable=True, default=False)
    virtual_url:           Mapped[Optional[str]]  = mapped_column(String(500), nullable=True)
    category:              Mapped[Optional[str]]  = mapped_column(String(100), nullable=True)
    recurrence:            Mapped[Optional[str]]  = mapped_column(String(20),  nullable=True, default="none")
    image_url:             Mapped[Optional[str]]  = mapped_column(String(500), nullable=True)
    registration_required: Mapped[Optional[bool]] = mapped_column(Boolean,     nullable=True, default=False)
    registration_url:      Mapped[Optional[str]]  = mapped_column(String(500), nullable=True)
    created_by:            Mapped[Optional[str]]  = mapped_column(String(36),  nullable=True)
    is_published:          Mapped[Optional[bool]] = mapped_column(Boolean,     nullable=True, default=False)
    created_at:            Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    updated_at:            Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
