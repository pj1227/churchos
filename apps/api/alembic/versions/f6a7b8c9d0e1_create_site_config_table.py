"""create site_config table

Revision ID: f6a7b8c9d0e1
Revises: e5f6a7b8c9d0
Create Date: 2026-05-29

What this migration does:
  Creates public.site_config — a key/value store for per-deployment
  configuration. Used by the connector framework (Phase 6) to store
  provider settings, and by Phase 5b for prayer_chain_email.

  Schema notes:
    - id: SERIAL (integer) — internal PK, not exposed via API
    - key: VARCHAR(200) — config key (e.g. "prayer_chain_email")
    - value: TEXT — config value (encrypted at rest for is_secret=true)
    - is_secret: BOOLEAN — if true, mask value in admin UI; encrypt at rest
    - is_json: BOOLEAN — if true, value is a JSON string; parse before use
    - Unique index on (church_id, key) — enforces one value per key per deployment
    - UPSERT pattern: INSERT ... ON CONFLICT (church_id, key) DO UPDATE

  NOTE: This table already existed in Supabase prior to Phase 5b.
  Stamp this migration rather than running it:
    alembic stamp f6a7b8c9d0e1

  Example rows:
    prayer_chain_email   | prayer@libbynaz.org | is_secret=false
    smtp_host            | smtp.office365.com  | is_secret=false
    smtp_password        | ***                 | is_secret=true
    ms365_client_secret  | ***                 | is_secret=true
"""
from alembic import op

revision      = "f6a7b8c9d0e1"
down_revision = "e5f6a7b8c9d0"
branch_labels = None
depends_on    = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE IF NOT EXISTS public.site_config (
            id         SERIAL       NOT NULL,
            church_id  VARCHAR(36)  NOT NULL REFERENCES public.churches(id) ON DELETE CASCADE,
            key        VARCHAR(200) NOT NULL,
            value      TEXT,
            is_secret  BOOLEAN      DEFAULT false,
            is_json    BOOLEAN      DEFAULT false,
            updated_at TIMESTAMPTZ  DEFAULT NOW(),
            CONSTRAINT site_config_pkey PRIMARY KEY (id)
        );
    """)
    op.execute("CREATE UNIQUE INDEX IF NOT EXISTS ix_site_config_church_key ON public.site_config(church_id, key);")
    op.execute("CREATE INDEX IF NOT EXISTS ix_site_config_church_id ON public.site_config(church_id);")


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS public.site_config;")
