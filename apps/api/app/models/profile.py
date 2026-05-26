"""
app/models/profile.py — User profile model.

What it does:
  Maps the public.profiles table. Every authenticated user gets one row
  here, created automatically by a Supabase trigger when they sign up.

Why it exists at this layer:
  Supabase manages auth.users (email, password hash, MFA state). We
  own public.profiles for app-level data: display name, role, church.
  Keeping these separate means we never touch the auth schema directly.

How it connects:
  - id is a UUID foreign key → auth.users.id (Supabase manages the FK).
  - Alembic creates this table via the initial migration.
  - RLS policies (applied in the migration) ensure users can only read
    their own row; admins can read all rows.
  - app/routers/profile.py queries this model via the DB session.
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Profile(Base):
    __tablename__ = "profiles"

    # Primary key mirrors auth.users.id — Supabase trigger sets this on signup
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # Denormalised from auth.users for convenience — kept in sync by trigger
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

    # App-level display name — user can change this independently of email
    display_name: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # RBAC role: superadmin | admin | staff | member | guest
    role: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="member",
        server_default="member",
    )

    # Church this profile belongs to (Phase 9: multi-church support)
    church_slug: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="libby-naz",
        server_default="libby-naz",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<Profile id={self.id} email={self.email} role={self.role}>"
