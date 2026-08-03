"""fix infinite recursion in RLS policies

Revision ID: k1l2m3n4o5p6
Revises: h8i9j0k1l2m3
Create Date: 2026-08-03

What this fixes
---------------
Every RLS policy in the project gates on the caller's role with an inline
subquery against public.profiles:

    EXISTS (SELECT 1 FROM public.profiles p WHERE p.id = auth.uid() AND ...)

On profiles itself that is self-referential, and Postgres raises

    42P17 infinite recursion detected in policy for relation "profiles"

The blast radius is wider than profiles. `churches` and `sermons` each have a
`public read USING (true)` policy, but their write policies are `FOR ALL` — and
a FOR ALL policy's USING clause is evaluated on SELECT as well. So an anonymous
read of either table walks into the profiles policy and returns HTTP 500.
Verified against the live project: anon GET /rest/v1/churches and
/rest/v1/sermons both return 42P17.

Migration h8i9j0k1l2m3 repeats the same pattern for site_config, announcements,
pages and sermon_sync_logs. It has not been applied yet (the database is at
g7h8i9j0k1l2), so this migration chains directly after it and repairs those
policies in the same upgrade — they are never left recursive in a state anyone
can query.

How the fix works
-----------------
public.current_user_role() is a SECURITY DEFINER function, so it runs as its
owner and RLS on profiles does not apply to it. Policies call the function
instead of selecting from profiles, so nothing recurses. search_path is pinned
because a SECURITY DEFINER function with a mutable search_path lets a caller
shadow `profiles` with their own table.

Write policies are also narrowed from FOR ALL to explicit INSERT/UPDATE/DELETE,
so a role check can never again be evaluated on a public read.

Apply:
    cd apps/api && alembic upgrade head
"""
from alembic import op

revision      = "k1l2m3n4o5p6"
down_revision = "h8i9j0k1l2m3"
branch_labels = None
depends_on    = None


# ---------------------------------------------------------------------------
# Helpers — non-recursive role checks
# ---------------------------------------------------------------------------

def _is_role(*roles: str) -> str:
    """Return a role check that does not touch public.profiles."""
    role_list = ", ".join(f"'{r}'" for r in roles)
    return f"public.current_user_role() IN ({role_list})"


ADMIN_ROLES = _is_role("admin", "superadmin")
STAFF_ROLES = _is_role("staff", "admin", "superadmin")
SUPERADMIN  = _is_role("superadmin")


def _write_policies(table: str, label: str, check: str) -> None:
    """Create INSERT/UPDATE/DELETE policies for `table`.

    Deliberately not FOR ALL — that form is also evaluated on SELECT, which is
    what broke public reads on churches and sermons.
    """
    op.execute(f"""
        CREATE POLICY "{table}: {label} can insert"
        ON public.{table} FOR INSERT
        WITH CHECK ({check});
    """)
    op.execute(f"""
        CREATE POLICY "{table}: {label} can update"
        ON public.{table} FOR UPDATE
        USING ({check})
        WITH CHECK ({check});
    """)
    op.execute(f"""
        CREATE POLICY "{table}: {label} can delete"
        ON public.{table} FOR DELETE
        USING ({check});
    """)


def _drop_write_policies(table: str, label: str) -> None:
    for command in ("insert", "update", "delete"):
        op.execute(
            f'DROP POLICY IF EXISTS "{table}: {label} can {command}" '
            f"ON public.{table};"
        )


# ---------------------------------------------------------------------------
# Upgrade
# ---------------------------------------------------------------------------

def upgrade() -> None:

    # -----------------------------------------------------------------------
    # The role lookup. SECURITY DEFINER is what breaks the recursion: the
    # function runs as its owner, so RLS on profiles is not applied to it.
    # -----------------------------------------------------------------------
    op.execute("""
        CREATE OR REPLACE FUNCTION public.current_user_role()
        RETURNS TEXT
        LANGUAGE sql
        STABLE
        SECURITY DEFINER
        SET search_path = public, pg_temp
        AS $$
            SELECT role FROM public.profiles WHERE id = auth.uid();
        $$;
    """)

    # anon needs EXECUTE too: a policy on a publicly readable table may call
    # this while evaluating an anonymous request. It returns NULL with no
    # session user, which fails every role check — no data is exposed.
    op.execute("REVOKE ALL ON FUNCTION public.current_user_role() FROM PUBLIC;")
    op.execute(
        "GRANT EXECUTE ON FUNCTION public.current_user_role() "
        "TO anon, authenticated, service_role;"
    )

    # -----------------------------------------------------------------------
    # profiles — the self-referential policy
    # -----------------------------------------------------------------------
    # The two "owner can ..." policies compare auth.uid() = id directly; they
    # never recurse and are left alone.
    op.execute('DROP POLICY IF EXISTS "profiles: admin can read all" ON public.profiles;')
    op.execute(f"""
        CREATE POLICY "profiles: admin can read all"
        ON public.profiles FOR SELECT
        USING ({ADMIN_ROLES});
    """)

    # -----------------------------------------------------------------------
    # sermons / churches — FOR ALL write policies that broke public reads
    # -----------------------------------------------------------------------
    op.execute('DROP POLICY IF EXISTS "sermons: staff can write" ON public.sermons;')
    _write_policies("sermons", "staff", STAFF_ROLES)

    op.execute('DROP POLICY IF EXISTS "churches: superadmin can write" ON public.churches;')
    _write_policies("churches", "superadmin", SUPERADMIN)

    # -----------------------------------------------------------------------
    # Tables from h8i9j0k1l2m3 — same recursive pattern, repaired here so the
    # two migrations are never applied in a broken intermediate state.
    # -----------------------------------------------------------------------

    # site_config holds connector secrets (grok_api_key, ms365_client_secret,
    # gloo_client_secret). Admin+ only, on both read and write — never public.
    op.execute('DROP POLICY IF EXISTS "site_config: admin can read" ON public.site_config;')
    op.execute('DROP POLICY IF EXISTS "site_config: admin can write" ON public.site_config;')
    op.execute(f"""
        CREATE POLICY "site_config: admin can read"
        ON public.site_config FOR SELECT
        USING ({ADMIN_ROLES});
    """)
    _write_policies("site_config", "admin", ADMIN_ROLES)

    # announcements / pages — published rows are public; staff+ write.
    op.execute(
        'DROP POLICY IF EXISTS "announcements: staff can write" ON public.announcements;'
    )
    _write_policies("announcements", "staff", STAFF_ROLES)

    op.execute('DROP POLICY IF EXISTS "pages: staff can write" ON public.pages;')
    _write_policies("pages", "staff", STAFF_ROLES)

    # sermon_sync_logs — internal audit trail, staff+ read only. Writes come
    # from the backend via the service key, which bypasses RLS.
    op.execute(
        'DROP POLICY IF EXISTS "sermon_sync_logs: staff can read" ON public.sermon_sync_logs;'
    )
    op.execute(f"""
        CREATE POLICY "sermon_sync_logs: staff can read"
        ON public.sermon_sync_logs FOR SELECT
        USING ({STAFF_ROLES});
    """)


# ---------------------------------------------------------------------------
# Downgrade — restores the recursive policies from h8i9j0k1l2m3 / 039f8b894c97
# ---------------------------------------------------------------------------

def downgrade() -> None:

    def _recursive_check(*roles: str) -> str:
        role_list = ", ".join(f"'{r}'" for r in roles)
        return f"""
            EXISTS (
                SELECT 1 FROM public.profiles p
                WHERE p.id = auth.uid()
                  AND p.role IN ({role_list})
            )
        """.strip()

    admin = _recursive_check("admin", "superadmin")
    staff = _recursive_check("staff", "admin", "superadmin")
    superadmin = _recursive_check("superadmin")

    for table, label in (
        ("sermons", "staff"),
        ("churches", "superadmin"),
        ("site_config", "admin"),
        ("announcements", "staff"),
        ("pages", "staff"),
    ):
        _drop_write_policies(table, label)

    op.execute('DROP POLICY IF EXISTS "profiles: admin can read all" ON public.profiles;')
    op.execute('DROP POLICY IF EXISTS "site_config: admin can read" ON public.site_config;')
    op.execute(
        'DROP POLICY IF EXISTS "sermon_sync_logs: staff can read" ON public.sermon_sync_logs;'
    )

    op.execute(f"""
        CREATE POLICY "profiles: admin can read all"
        ON public.profiles FOR SELECT
        USING ({admin});
    """)
    op.execute(f"""
        CREATE POLICY "sermons: staff can write"
        ON public.sermons FOR ALL
        USING ({staff});
    """)
    op.execute(f"""
        CREATE POLICY "churches: superadmin can write"
        ON public.churches FOR ALL
        USING ({superadmin});
    """)
    op.execute(f"""
        CREATE POLICY "site_config: admin can read"
        ON public.site_config FOR SELECT
        USING ({admin});
    """)
    op.execute(f"""
        CREATE POLICY "site_config: admin can write"
        ON public.site_config FOR ALL
        USING ({admin});
    """)
    op.execute(f"""
        CREATE POLICY "announcements: staff can write"
        ON public.announcements FOR ALL
        USING ({staff});
    """)
    op.execute(f"""
        CREATE POLICY "pages: staff can write"
        ON public.pages FOR ALL
        USING ({staff});
    """)
    op.execute(f"""
        CREATE POLICY "sermon_sync_logs: staff can read"
        ON public.sermon_sync_logs FOR SELECT
        USING ({staff});
    """)

    op.execute("DROP FUNCTION IF EXISTS public.current_user_role();")
