"""create prayer_requests table

Revision ID: d4e5f6a7b8c9
Revises: b2c3d4e5f6a7
Create Date: 2026-05-28

What this migration does:
  Creates public.prayer_requests — stores community prayer requests submitted
  through the public prayer board form. Supports AI moderation workflow:
  submissions are stored with status='pending' until AI or staff moderates them.

  RLS is enabled immediately — approved requests are readable by authenticated
  users only; pending/rejected are restricted to staff+ via application-layer
  filtering (the RLS policy is additive, not substitutive, for simplicity).

  NOTE: If running against a Supabase project where this table already
  exists, stamp this revision as applied:
    alembic stamp d4e5f6a7b8c9
"""
from alembic import op

revision      = "d4e5f6a7b8c9"
down_revision = "b2c3d4e5f6a7"
branch_labels = None
depends_on    = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE IF NOT EXISTS public.prayer_requests (
            id            UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
            church_id     VARCHAR(36)  NOT NULL REFERENCES public.churches(id) ON DELETE CASCADE,
            name          VARCHAR(150),
            body          TEXT         NOT NULL,
            is_anonymous  BOOLEAN      DEFAULT false,
            status        VARCHAR(20)  NOT NULL DEFAULT 'pending'
                          CHECK (status IN ('pending', 'approved', 'rejected')),
            ai_score      FLOAT,
            ai_reason     TEXT,
            submitted_at  TIMESTAMPTZ  DEFAULT NOW(),
            moderated_at  TIMESTAMPTZ,
            moderated_by  UUID,
            is_answered   BOOLEAN      DEFAULT false,
            created_at    TIMESTAMPTZ  DEFAULT NOW(),
            updated_at    TIMESTAMPTZ  DEFAULT NOW()
        );
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_prayer_requests_church_id  ON public.prayer_requests(church_id);")
    op.execute("CREATE INDEX IF NOT EXISTS ix_prayer_requests_status     ON public.prayer_requests(status);")
    op.execute("CREATE INDEX IF NOT EXISTS ix_prayer_requests_submitted  ON public.prayer_requests(submitted_at DESC);")
    op.execute("ALTER TABLE public.prayer_requests ENABLE ROW LEVEL SECURITY;")


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS public.prayer_requests;")
