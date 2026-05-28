"""create sermons table

Revision ID: a1b2c3d4e5f6
Revises: 039f8b894c97
Create Date: 2026-05-27

What this migration does:
  Creates public.sermons — the Logos-synced sermon content table.
  Designed for multi-church use with a church_id FK to public.churches.

  NOTE: If running against a Supabase project where this table already
  exists (e.g. created via another thread), stamp this revision as applied:
    alembic stamp a1b2c3d4e5f6
"""
from alembic import op

revision      = "a1b2c3d4e5f6"
down_revision = "039f8b894c97"
branch_labels = None
depends_on    = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE IF NOT EXISTS public.sermons (
            id                   VARCHAR(36)  PRIMARY KEY,
            church_id            VARCHAR(36)  NOT NULL REFERENCES public.churches(id) ON DELETE CASCADE,
            logos_id             VARCHAR(100) UNIQUE,
            logos_url            VARCHAR(500),
            logos_embed_url      VARCHAR(500),
            logos_series_id      VARCHAR(100),
            title                VARCHAR(300) NOT NULL,
            speaker_name         VARCHAR(150) DEFAULT '',
            series               VARCHAR(200),
            date                 VARCHAR(10)  NOT NULL,
            description          TEXT,
            notes                TEXT,
            scripture_reference  VARCHAR(300),
            thumbnail_url        VARCHAR(500),
            series_thumbnail_url VARCHAR(500),
            duration_seconds     INTEGER,
            tags                 TEXT,
            has_audio            BOOLEAN DEFAULT false,
            has_video            BOOLEAN DEFAULT false,
            has_slides           BOOLEAN DEFAULT false,
            is_published         BOOLEAN DEFAULT true,
            logos_published_at   TIMESTAMPTZ,
            logos_updated_at     TIMESTAMPTZ,
            first_synced_at      TIMESTAMPTZ DEFAULT NOW(),
            last_synced_at       TIMESTAMPTZ DEFAULT NOW(),
            created_at           TIMESTAMPTZ DEFAULT NOW(),
            updated_at           TIMESTAMPTZ DEFAULT NOW()
        );
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_sermons_church_id ON public.sermons(church_id);")
    op.execute("CREATE INDEX IF NOT EXISTS ix_sermons_date      ON public.sermons(date);")
    op.execute("CREATE INDEX IF NOT EXISTS ix_sermons_logos_id  ON public.sermons(logos_id);")
    op.execute("ALTER TABLE public.sermons ENABLE ROW LEVEL SECURITY;")


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS public.sermons;")
