"""create prayer_updates table

Revision ID: g7h8i9j0k1l2
Revises: f6a7b8c9d0e1
Create Date: 2026-05-29

What this migration does:
  Creates public.prayer_updates — stores staff-posted updates on prayer
  requests. Allows the prayer team to post "God answered this prayer" or
  progress notes visible to members viewing the prayer board.

  Schema notes:
    - id: UUID with DB default
    - prayer_request_id: FK to prayer_requests (CASCADE delete)
    - body: the update text
    - created_by: UUID of the staff member who posted the update
    - created_at: timestamp
    - is_public: if true, visible on public prayer board; if false, staff only

  Apply in Supabase SQL editor if running for the first time:
    (see upgrade() below)
  Or stamp if applied manually:
    alembic stamp g7h8i9j0k1l2
"""
from alembic import op

revision      = "g7h8i9j0k1l2"
down_revision = "f6a7b8c9d0e1"
branch_labels = None
depends_on    = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE IF NOT EXISTS public.prayer_updates (
            id                UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
            prayer_request_id UUID        NOT NULL REFERENCES public.prayer_requests(id) ON DELETE CASCADE,
            body              TEXT        NOT NULL,
            created_by        UUID        NOT NULL,
            is_public         BOOLEAN     NOT NULL DEFAULT true,
            created_at        TIMESTAMPTZ DEFAULT NOW()
        );
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_prayer_updates_request_id ON public.prayer_updates(prayer_request_id);")
    op.execute("CREATE INDEX IF NOT EXISTS ix_prayer_updates_created_at ON public.prayer_updates(created_at DESC);")
    op.execute("ALTER TABLE public.prayer_updates ENABLE ROW LEVEL SECURITY;")


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS public.prayer_updates;")
