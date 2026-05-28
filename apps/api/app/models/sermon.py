"""
models/sermon.py — SQLAlchemy ORM model for public.sermons.

Mirrors the existing Supabase table exactly. Sermons are primarily
populated by the Logos sync process; the admin dashboard allows editing
human-controlled fields (description, notes, is_published, tags, etc.).

How it connects:
  - app/models/base.py supplies DeclarativeBase
  - app/crud/sermons.py queries this model
  - alembic/env.py imports Base.metadata for migration autogeneration
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Sermon(Base):
    __tablename__ = "sermons"

    id:                   Mapped[str]            = mapped_column(String(36),  primary_key=True)
    church_id:            Mapped[str]            = mapped_column(String(36),  ForeignKey("churches.id", ondelete="CASCADE"), nullable=False, index=True)
    logos_id:             Mapped[Optional[str]]  = mapped_column(String(100), nullable=True, unique=True, index=True)
    logos_url:            Mapped[Optional[str]]  = mapped_column(String(500), nullable=True)
    logos_embed_url:      Mapped[Optional[str]]  = mapped_column(String(500), nullable=True)
    logos_series_id:      Mapped[Optional[str]]  = mapped_column(String(100), nullable=True)
    title:                Mapped[str]            = mapped_column(String(300), nullable=False)
    speaker_name:         Mapped[Optional[str]]  = mapped_column(String(150), nullable=True, default="")
    series:               Mapped[Optional[str]]  = mapped_column(String(200), nullable=True)
    date:                 Mapped[str]            = mapped_column(String(10),  nullable=False, index=True)
    description:          Mapped[Optional[str]]  = mapped_column(Text,        nullable=True)
    notes:                Mapped[Optional[str]]  = mapped_column(Text,        nullable=True)
    scripture_reference:  Mapped[Optional[str]]  = mapped_column(String(300), nullable=True)
    thumbnail_url:        Mapped[Optional[str]]  = mapped_column(String(500), nullable=True)
    series_thumbnail_url: Mapped[Optional[str]]  = mapped_column(String(500), nullable=True)
    duration_seconds:     Mapped[Optional[int]]  = mapped_column(Integer,     nullable=True)
    tags:                 Mapped[Optional[str]]  = mapped_column(Text,        nullable=True)
    has_audio:            Mapped[Optional[bool]] = mapped_column(Boolean,     nullable=True, default=False)
    has_video:            Mapped[Optional[bool]] = mapped_column(Boolean,     nullable=True, default=False)
    has_slides:           Mapped[Optional[bool]] = mapped_column(Boolean,     nullable=True, default=False)
    is_published:         Mapped[Optional[bool]] = mapped_column(Boolean,     nullable=True, default=True)
    logos_published_at:   Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    logos_updated_at:     Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    first_synced_at:      Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_synced_at:       Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at:           Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    updated_at:           Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
