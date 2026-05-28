"""create church_events table

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-05-27

NOTE: If running against a Supabase project where this table already
exists, stamp this revision as applied:
  alembic stamp b2c3d4e5f6a7
"""
from alembic import op

revision      = "b2c3d4e5f6a7"
down_revision = "a1b2c3d4e5f6"
branch_labels = None
depends_on    = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE IF NOT EXISTS public.church_events (
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


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS public.church_events;")
