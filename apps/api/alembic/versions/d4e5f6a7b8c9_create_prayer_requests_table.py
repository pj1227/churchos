"""create prayer_requests table

Revision ID: d4e5f6a7b8c9
Revises: b2c3d4e5f6a7
Create Date: 2026-05-28

What this migration does:
  Creates public.prayer_requests — community prayer requests submitted through
  the public prayer board form, with AI moderation and staff review workflow.

  Schema notes:
    - id: UUID with DB default (gen_random_uuid()) — no application-side generation
    - body: the prayer text (clean, unambiguous field name)
    - name / email: submitter identity (email optional, for follow-up only)
    - ai_score / ai_reason: AI moderation result
    - moderated_at / moderated_by: staff audit trail
    - prayer_count: community upvotes (populated in a future phase)
    - is_answered: submitter or staff can mark a prayer as answered
    - expires_at: optional expiry for time-sensitive requests
    - CHECK constraint on status ensures only valid values are stored

  If recreating an existing table, run in Supabase SQL editor first:
    DROP TABLE IF EXISTS public.prayer_requests CASCADE;
  Then apply this migration:
    alembic upgrade d4e5f6a7b8c9
  Or stamp if applied manually:
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
            email         VARCHAR(254),
            body          TEXT         NOT NULL,
            is_anonymous  BOOLEAN      NOT NULL DEFAULT false,
            status        VARCHAR(20)  NOT NULL DEFAULT 'pending'
                          CHECK (status IN ('pending', 'approved', 'rejected')),
            ai_score      FLOAT,
            ai_reason     TEXT,
            prayer_count  INTEGER      NOT NULL DEFAULT 0,
            submitted_at  TIMESTAMPTZ  DEFAULT NOW(),
            moderated_at  TIMESTAMPTZ,
            moderated_by  UUID,
            is_answered   BOOLEAN      NOT NULL DEFAULT false,
            expires_at    TIMESTAMPTZ,
            created_at    TIMESTAMPTZ  DEFAULT NOW(),
            updated_at    TIMESTAMPTZ  DEFAULT NOW()
        );
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_prayer_requests_church_id ON public.prayer_requests(church_id);")
    op.execute("CREATE INDEX IF NOT EXISTS ix_prayer_requests_status    ON public.prayer_requests(status);")
    op.execute("CREATE INDEX IF NOT EXISTS ix_prayer_requests_submitted ON public.prayer_requests(submitted_at DESC);")
    op.execute("ALTER TABLE public.prayer_requests ENABLE ROW LEVEL SECURITY;")


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS public.prayer_requests;")
