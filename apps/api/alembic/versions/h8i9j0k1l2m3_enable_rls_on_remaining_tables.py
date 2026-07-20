"""enable RLS on remaining public tables

Revision ID: h8i9j0k1l2m3
Revises: g7h8i9j0k1l2
Create Date: 2026-07-14

What this migration does:
  Resolves the Supabase "rls_disabled_in_public" security alert by enabling
  Row-Level Security on every public table that was previously unrestricted.
  This prevents anonymous callers from reading or mutating data via the anon
  key / PostgREST without going through the FastAPI backend.

  The API backend uses SUPABASE_SERVICE_KEY which bypasses RLS entirely, so
  backend behaviour is unaffected. These policies gate only direct PostgREST
  calls (anon key, authenticated JWT from a browser client, etc.).

  Tables addressed:
    site_config      — key/value config; contains secrets (SMTP passwords,
                       MS365 client secrets). Admin+ only. NO public access.
    announcements    — church announcements. Public read for published rows;
                       staff+ write.
    pages            — CMS pages. Public read for published rows; staff+ write.
    sermon_sync_logs — internal Logos sync audit log. Staff+ read only.
                       No public access. Service role writes via backend.

  alembic_version is a system table managed by Alembic — it cannot have RLS
  enabled (Postgres does not allow RLS on system catalog tables). It is not
  accessible via the PostgREST REST API, so it is not a security concern.

  Apply this migration:
    cd apps/api && alembic upgrade h8i9j0k1l2m3

  Or stamp if applied manually in the Supabase SQL editor:
    alembic stamp h8i9j0k1l2m3
"""
from alembic import op

revision      = "h8i9j0k1l2m3"
down_revision = "g7h8i9j0k1l2"
branch_labels = None
depends_on    = None


# ---------------------------------------------------------------------------
# Helper — inline role check used in multiple policies
# ---------------------------------------------------------------------------

def _role_check(*roles: str) -> str:
    """Return a USING clause subquery that checks the caller's profile role."""
    role_list = ", ".join(f"'{r}'" for r in roles)
    return f"""
        EXISTS (
            SELECT 1 FROM public.profiles p
            WHERE p.id = auth.uid()
              AND p.role IN ({role_list})
        )
    """.strip()


ADMIN_ROLES   = _role_check("admin", "superadmin")
STAFF_ROLES   = _role_check("staff", "admin", "superadmin")


# ---------------------------------------------------------------------------
# Upgrade
# ---------------------------------------------------------------------------

def upgrade() -> None:

    # -----------------------------------------------------------------------
    # site_config — secrets live here; NEVER public
    # -----------------------------------------------------------------------
    op.execute("ALTER TABLE public.site_config ENABLE ROW LEVEL SECURITY;")

    op.execute(f"""
        CREATE POLICY "site_config: admin can read"
        ON public.site_config FOR SELECT
        USING ({ADMIN_ROLES});
    """)

    op.execute(f"""
        CREATE POLICY "site_config: admin can write"
        ON public.site_config FOR ALL
        USING ({ADMIN_ROLES});
    """)

    # -----------------------------------------------------------------------
    # announcements — public read for is_published=true; staff+ write
    # -----------------------------------------------------------------------
    op.execute("""
        ALTER TABLE public.announcements ENABLE ROW LEVEL SECURITY;
    """)

    op.execute("""
        CREATE POLICY "announcements: public read published"
        ON public.announcements FOR SELECT
        USING (is_published = true);
    """)

    op.execute(f"""
        CREATE POLICY "announcements: staff can write"
        ON public.announcements FOR ALL
        USING ({STAFF_ROLES});
    """)

    # -----------------------------------------------------------------------
    # pages — public read for published; staff+ write
    # -----------------------------------------------------------------------
    op.execute("ALTER TABLE public.pages ENABLE ROW LEVEL SECURITY;")

    op.execute("""
        CREATE POLICY "pages: public read published"
        ON public.pages FOR SELECT
        USING (is_published = true);
    """)

    op.execute(f"""
        CREATE POLICY "pages: staff can write"
        ON public.pages FOR ALL
        USING ({STAFF_ROLES});
    """)

    # -----------------------------------------------------------------------
    # sermon_sync_logs — internal audit log; staff+ read; no public access
    # -----------------------------------------------------------------------
    op.execute("ALTER TABLE public.sermon_sync_logs ENABLE ROW LEVEL SECURITY;")

    op.execute(f"""
        CREATE POLICY "sermon_sync_logs: staff can read"
        ON public.sermon_sync_logs FOR SELECT
        USING ({STAFF_ROLES});
    """)

    # No INSERT/UPDATE/DELETE policy — backend writes via service role (bypasses RLS).
    # Direct writes from a browser JWT are intentionally blocked.


# ---------------------------------------------------------------------------
# Downgrade
# ---------------------------------------------------------------------------

def downgrade() -> None:
    # sermon_sync_logs
    op.execute('DROP POLICY IF EXISTS "sermon_sync_logs: staff can read" ON public.sermon_sync_logs;')
    op.execute("ALTER TABLE public.sermon_sync_logs DISABLE ROW LEVEL SECURITY;")

    # pages
    op.execute('DROP POLICY IF EXISTS "pages: public read published" ON public.pages;')
    op.execute('DROP POLICY IF EXISTS "pages: staff can write" ON public.pages;')
    op.execute("ALTER TABLE public.pages DISABLE ROW LEVEL SECURITY;")

    # announcements
    op.execute('DROP POLICY IF EXISTS "announcements: public read published" ON public.announcements;')
    op.execute('DROP POLICY IF EXISTS "announcements: staff can write" ON public.announcements;')
    op.execute("ALTER TABLE public.announcements DISABLE ROW LEVEL SECURITY;")

    # site_config
    op.execute('DROP POLICY IF EXISTS "site_config: admin can read" ON public.site_config;')
    op.execute('DROP POLICY IF EXISTS "site_config: admin can write" ON public.site_config;')
    op.execute("ALTER TABLE public.site_config DISABLE ROW LEVEL SECURITY;")
