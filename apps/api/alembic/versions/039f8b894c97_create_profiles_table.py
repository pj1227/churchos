"""create profiles table

Revision ID: 039f8b894c97
Revises:
Create Date: 2026-05-23

What this migration does:
  1. Drops the old `users` table — varchar PKs, incompatible with Supabase auth.
  2. Creates public.profiles with UUID PK mirroring auth.users.id.
  3. Enables RLS on profiles, sermons, and churches.
  4. Adds RLS policies for each table.
  5. Creates a trigger so a profile row is created on Supabase user signup.
"""
from alembic import op

revision = "039f8b894c97"
down_revision = "003_site_config"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Drop old incompatible users table (empty, varchar PKs)
    op.execute("DROP TABLE IF EXISTS public.users CASCADE;")

    # 2. Create profiles table
    op.execute("""
        CREATE TABLE IF NOT EXISTS public.profiles (
            id           UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
            email        TEXT NOT NULL UNIQUE,
            display_name TEXT,
            role         TEXT NOT NULL DEFAULT 'member'
                             CHECK (role IN ('superadmin','admin','staff','member','guest')),
            church_slug  TEXT NOT NULL DEFAULT 'libby-naz',
            created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );
    """)

    # 3. Enable RLS on all public tables
    op.execute("ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE public.sermons  ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE public.churches ENABLE ROW LEVEL SECURITY;")

    # 4a. Profiles policies
    op.execute("""
        CREATE POLICY "profiles: owner can read own"
        ON public.profiles FOR SELECT
        USING (auth.uid() = id);
    """)
    op.execute("""
        CREATE POLICY "profiles: owner can update own"
        ON public.profiles FOR UPDATE
        USING (auth.uid() = id);
    """)
    op.execute("""
        CREATE POLICY "profiles: admin can read all"
        ON public.profiles FOR SELECT
        USING (
            EXISTS (
                SELECT 1 FROM public.profiles p
                WHERE p.id = auth.uid()
                  AND p.role IN ('admin', 'superadmin')
            )
        );
    """)

    # 4b. Sermons policies
    op.execute("""
        CREATE POLICY "sermons: public read"
        ON public.sermons FOR SELECT
        USING (true);
    """)
    op.execute("""
        CREATE POLICY "sermons: staff can write"
        ON public.sermons FOR ALL
        USING (
            EXISTS (
                SELECT 1 FROM public.profiles p
                WHERE p.id = auth.uid()
                  AND p.role IN ('staff', 'admin', 'superadmin')
            )
        );
    """)

    # 4c. Churches policies
    op.execute("""
        CREATE POLICY "churches: public read"
        ON public.churches FOR SELECT
        USING (true);
    """)
    op.execute("""
        CREATE POLICY "churches: superadmin can write"
        ON public.churches FOR ALL
        USING (
            EXISTS (
                SELECT 1 FROM public.profiles p
                WHERE p.id = auth.uid()
                  AND p.role = 'superadmin'
            )
        );
    """)

    # 5. Trigger: auto-create profile row when a user signs up via Supabase Auth
    op.execute("""
        CREATE OR REPLACE FUNCTION public.handle_new_user()
        RETURNS TRIGGER
        LANGUAGE plpgsql
        SECURITY DEFINER
        SET search_path = public
        AS $$
        BEGIN
            INSERT INTO public.profiles (id, email)
            VALUES (NEW.id, NEW.email)
            ON CONFLICT (id) DO NOTHING;
            RETURN NEW;
        END;
        $$;
    """)
    op.execute("""
        DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
        CREATE TRIGGER on_auth_user_created
            AFTER INSERT ON auth.users
            FOR EACH ROW
            EXECUTE FUNCTION public.handle_new_user();
    """)


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;")
    op.execute("DROP FUNCTION IF EXISTS public.handle_new_user();")
    op.execute('DROP POLICY IF EXISTS "profiles: owner can read own" ON public.profiles;')
    op.execute('DROP POLICY IF EXISTS "profiles: owner can update own" ON public.profiles;')
    op.execute('DROP POLICY IF EXISTS "profiles: admin can read all" ON public.profiles;')
    op.execute('DROP POLICY IF EXISTS "sermons: public read" ON public.sermons;')
    op.execute('DROP POLICY IF EXISTS "sermons: staff can write" ON public.sermons;')
    op.execute('DROP POLICY IF EXISTS "churches: public read" ON public.churches;')
    op.execute('DROP POLICY IF EXISTS "churches: superadmin can write" ON public.churches;')
    op.execute("ALTER TABLE public.sermons  DISABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE public.churches DISABLE ROW LEVEL SECURITY;")
    op.execute("DROP TABLE IF EXISTS public.profiles;")
