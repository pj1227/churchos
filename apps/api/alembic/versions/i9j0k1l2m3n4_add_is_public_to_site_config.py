"""add is_public to site_config

Revision ID: i9j0k1l2m3n4
Revises: h8i9j0k1l2m3
Create Date: 2026-07-28

What this migration does:
  Adds public.site_config.is_public (BOOLEAN, default false).

  Why: site_config was built for connector/infra settings (email provider,
  AI provider, prayer chain email) which are all staff+-gated reads. The
  new site-content CMS layer (church name, address, contact info, page
  copy) reuses the same table but needs a subset of rows readable by the
  public website without auth. is_public opts a specific row into that —
  defaulting to false keeps every existing row private with no behavior
  change. GET /site-config/public (see app/routers/site_config.py) only
  ever returns rows where is_public=true AND is_secret=false.
"""
from alembic import op

revision      = "i9j0k1l2m3n4"
down_revision = "h8i9j0k1l2m3"
branch_labels = None
depends_on    = None


def upgrade() -> None:
    op.execute("""
        ALTER TABLE public.site_config
        ADD COLUMN IF NOT EXISTS is_public BOOLEAN NOT NULL DEFAULT false;
    """)


def downgrade() -> None:
    op.execute("ALTER TABLE public.site_config DROP COLUMN IF EXISTS is_public;")
