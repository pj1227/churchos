"""church_events — migrate id to UUID

Revision ID: e5f6a7b8c9d0
Revises: d4e5f6a7b8c9
Create Date: 2026-05-28

What this migration does:
  Migrates public.church_events.id from VARCHAR(36) to UUID with a DB-generated
  default. All future tables use UUID PKs; this brings church_events in line.

  Safe because:
    - church_events table is empty (no events have been created yet)
    - No external system (like Logos) assigns IDs to events — we generate them
    - The existing FK in prayer_requests does not reference church_events

  Why we don't migrate churches or sermons:
    - churches.id = "default" is a meaningful singleton identifier; leave it
    - sermons.id is assigned by the Logos sync process; changing the PK type
      would risk breaking sync — leave it as VARCHAR(36)

  NOTE: If running against a Supabase project that already has this change,
  stamp this revision:
    alembic stamp e5f6a7b8c9d0
"""
from alembic import op


revision      = "e5f6a7b8c9d0"
down_revision = "d4e5f6a7b8c9"
branch_labels = None
depends_on    = None


def upgrade() -> None:
    # Drop and recreate is safe — table is empty and no external IDs reference it.
    op.execute("DROP TABLE IF EXISTS public.church_events CASCADE;")
    op.execute("""
        CREATE TABLE public.church_events (
            id                    UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
            church_id             VARCHAR(36)  NOT NULL REFERENCES public.churches(id) ON DELETE CASCADE,
            title                 VARCHAR(300) NOT NULL,
            description           TEXT,
            start_at              TIMESTAMPTZ  NOT NULL,
            end_at                TIMESTAMPTZ  NOT NULL,
            all_day               BOOLEAN      NOT NULL DEFAULT false,
            location              VARCHAR(300),
            is_virtual            BOOLEAN      NOT NULL DEFAULT false,
            virtual_url           VARCHAR(500),
            category              VARCHAR(100),
            recurrence            VARCHAR(20)  NOT NULL DEFAULT 'none',
            image_url             VARCHAR(500),
            registration_required BOOLEAN      NOT NULL DEFAULT false,
            registration_url      VARCHAR(500),
            created_by            UUID,
            is_published          BOOLEAN      NOT NULL DEFAULT false,
            created_at            TIMESTAMPTZ  DEFAULT NOW(),
            updated_at            TIMESTAMPTZ  DEFAULT NOW()
        );
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_events_church_id ON public.church_events(church_id);")
    op.execute("CREATE INDEX IF NOT EXISTS ix_events_start_at  ON public.church_events(start_at);")
    op.execute("ALTER TABLE public.church_events ENABLE ROW LEVEL SECURITY;")


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS public.church_events CASCADE;")
    op.execute("""
        CREATE TABLE public.church_events (
            id                    VARCHAR(36)  PRIMARY KEY,
            church_id             VARCHAR(36)  NOT NULL REFERENCES public.churches(id) ON DELETE CASCADE,
            title                 VARCHAR(300) NOT NULL,
            description           TEXT,
            start_at              TIMESTAMPTZ  NOT NULL,
            end_at                TIMESTAMPTZ  NOT NULL,
            all_day               BOOLEAN      DEFAULT false,
            location              VARCHAR(300),
            is_virtual            BOOLEAN      DEFAULT false,
            virtual_url           VARCHAR(500),
            category              VARCHAR(100),
            recurrence            VARCHAR(20)  DEFAULT 'none',
            image_url             VARCHAR(500),
            registration_required BOOLEAN      DEFAULT false,
            registration_url      VARCHAR(500),
            created_by            VARCHAR(36),
            is_published          BOOLEAN      DEFAULT false,
            created_at            TIMESTAMPTZ  DEFAULT NOW(),
            updated_at            TIMESTAMPTZ  DEFAULT NOW()
        );
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_events_church_id ON public.church_events(church_id);")
    op.execute("CREATE INDEX IF NOT EXISTS ix_events_start_at  ON public.church_events(start_at);")
    op.execute("ALTER TABLE public.church_events ENABLE ROW LEVEL SECURITY;")
