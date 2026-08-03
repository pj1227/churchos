"""
test_rls_recursion_fix.py — TDD tests for migration k1l2m3n4o5p6.

## The bug

Every RLS policy in the project checks the caller's role with an inline
subquery:

    EXISTS (SELECT 1 FROM public.profiles p WHERE p.id = auth.uid() AND ...)

On `public.profiles` itself that is self-referential: evaluating the
"admin can read all" policy requires selecting from profiles, which requires
evaluating the policy. Postgres detects it and raises:

    42P17 infinite recursion detected in policy for relation "profiles"

It is not confined to profiles. `churches` and `sermons` both have a
`public read USING (true)` policy, yet both return HTTP 500 to an anonymous
caller, because their write policies are `FOR ALL` — a FOR ALL policy's USING
clause is evaluated on SELECT too, and it reaches into profiles.

Verified against the live project before writing this: anon GET on
/rest/v1/churches and /rest/v1/sermons both return 42P17.

## Why it has not bitten harder yet

Migration h8i9j0k1l2m3 uses the same pattern for site_config, announcements,
pages and sermon_sync_logs — and is not yet applied (alembic_version is at
g7h8i9j0k1l2). Applying it unchanged would extend the recursion to four more
tables. So the fix has to land with it, not after it.

## The fix these tests describe

A SECURITY DEFINER function, `public.current_user_role()`, reads the caller's
role while bypassing RLS on profiles, so no policy needs to select from
profiles. Every policy is rewritten to call it, and the `FOR ALL` write
policies are narrowed to INSERT/UPDATE/DELETE so they stop being evaluated on
reads.

How it connects:
  - Loads alembic/versions/k1l2m3n4o5p6_fix_profiles_policy_recursion.py
  - Runs upgrade()/downgrade() against a mock op that captures SQL
  - Mirrors the contract-test style of tests/test_rls_migration.py
"""
import importlib.util
import re
from pathlib import Path
from unittest.mock import MagicMock, patch


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

VERSIONS_DIR = Path(__file__).parent.parent / "alembic" / "versions"
MIGRATION_PATH = VERSIONS_DIR / "k1l2m3n4o5p6_fix_profiles_policy_recursion.py"

# The helper that replaces every inline profiles subquery.
ROLE_FN = "public.current_user_role()"


def load_migration():
    spec = importlib.util.spec_from_file_location("migration_rls_fix", MIGRATION_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def capture_sql(migration_mod, direction: str = "upgrade") -> list[str]:
    """Run upgrade()/downgrade() with a mock op; return the SQL executed."""
    executed: list[str] = []
    mock_op = MagicMock()
    mock_op.execute.side_effect = lambda sql: executed.append(sql.strip())

    with patch.object(migration_mod, "op", mock_op):
        getattr(migration_mod, direction)()

    return executed


def policy_statements(sql_list: list[str]) -> list[str]:
    """Just the CREATE POLICY statements."""
    return [s for s in sql_list if "CREATE POLICY" in s.upper()]


# ---------------------------------------------------------------------------
# Migration wiring
# ---------------------------------------------------------------------------

class TestMigrationExists:
    def test_migration_file_exists(self):
        assert MIGRATION_PATH.exists(), (
            f"Migration file not found: {MIGRATION_PATH}\n"
            "Create the recursion fix migration."
        )

    def test_migration_has_correct_revision(self):
        assert load_migration().revision == "k1l2m3n4o5p6"

    def test_migration_chains_from_the_rls_migration(self):
        """Must run after h8i9j0k1l2m3, which creates the policies it repairs."""
        assert load_migration().down_revision == "h8i9j0k1l2m3"

    def test_revision_id_is_unique_in_the_versions_dir(self):
        """A duplicate revision id gives alembic two heads and a broken upgrade."""
        ids = []
        for path in VERSIONS_DIR.glob("*.py"):
            match = re.search(r'^revision\s*=\s*["\'](\w+)["\']', path.read_text(), re.M)
            if match:
                ids.append(match.group(1))
        assert len(ids) == len(set(ids)), f"Duplicate revision ids: {ids}"


# ---------------------------------------------------------------------------
# The role helper
# ---------------------------------------------------------------------------

class TestRoleHelperFunction:
    def setup_method(self):
        self.sql = "\n".join(capture_sql(load_migration()))

    def test_creates_the_role_lookup_function(self):
        assert "current_user_role" in self.sql

    def test_function_is_security_definer(self):
        """Without SECURITY DEFINER the function runs as the caller, RLS on
        profiles applies again, and the recursion comes straight back."""
        assert re.search(r"SECURITY\s+DEFINER", self.sql, re.I), (
            "current_user_role() must be SECURITY DEFINER to bypass RLS on profiles."
        )

    def test_function_pins_search_path(self):
        """A SECURITY DEFINER function with a mutable search_path is a
        privilege-escalation vector — a caller could shadow `profiles`."""
        assert re.search(r"SET\s+search_path", self.sql, re.I), (
            "SECURITY DEFINER function must pin search_path."
        )


# ---------------------------------------------------------------------------
# The recursion itself — the point of this migration
# ---------------------------------------------------------------------------

class TestNoRecursivePolicies:
    def setup_method(self):
        self.policies = policy_statements(capture_sql(load_migration()))

    def test_migration_creates_policies(self):
        assert self.policies, "Migration creates no policies"

    def test_no_policy_selects_from_profiles(self):
        """This is the regression guard. Any policy that reads public.profiles
        re-introduces 42P17 the moment it is evaluated on profiles itself, or
        on a table whose policy chain reaches profiles."""
        for statement in self.policies:
            assert not re.search(r"FROM\s+public\.profiles", statement, re.I), (
                "Policy selects from public.profiles — this is the recursion "
                f"the migration exists to remove. Use {ROLE_FN}:\n{statement}"
            )

    def test_role_checks_go_through_the_helper(self):
        """Every policy that gates on a role must call the helper."""
        role_gated = [
            p for p in self.policies
            if re.search(r"'(?:staff|admin|superadmin)'", p, re.I)
        ]
        assert role_gated, "No role-gated policies found"
        for statement in role_gated:
            assert "current_user_role" in statement, (
                f"Role-gated policy does not use {ROLE_FN}:\n{statement}"
            )


class TestWritePoliciesDoNotBurdenReads:
    """`FOR ALL` policies are evaluated on SELECT.

    That is how a role check on churches/sermons — tables that are supposed to
    be publicly readable — ended up failing anonymous reads. Write policies
    must name the write commands explicitly.
    """

    def setup_method(self):
        self.policies = policy_statements(capture_sql(load_migration()))

    def test_no_for_all_policies_created(self):
        for statement in self.policies:
            assert not re.search(r"\bFOR\s+ALL\b", statement, re.I), (
                "FOR ALL policy created — its USING clause will be evaluated on "
                f"SELECT. Use FOR INSERT / UPDATE / DELETE:\n{statement}"
            )

    def test_drops_the_existing_for_all_policies(self):
        """The FOR ALL policies from 039f8b894c97 must actually be removed."""
        sql = "\n".join(capture_sql(load_migration())).lower()
        for policy in ("sermons: staff can write", "churches: superadmin can write"):
            assert f'drop policy if exists "{policy}"' in sql, (
                f'Migration does not drop the existing "{policy}" policy.'
            )

    def test_insert_policies_use_with_check(self):
        """FOR INSERT takes WITH CHECK, not USING — a USING clause on an INSERT
        policy is silently ineffective."""
        for statement in self.policies:
            if re.search(r"\bFOR\s+INSERT\b", statement, re.I):
                assert re.search(r"WITH\s+CHECK", statement, re.I), (
                    f"INSERT policy without WITH CHECK:\n{statement}"
                )


# ---------------------------------------------------------------------------
# Public reads must survive the fix
# ---------------------------------------------------------------------------

class TestPublicReadsStillWork:
    def setup_method(self):
        self.sql = "\n".join(capture_sql(load_migration())).lower()

    def test_churches_keeps_a_public_read_policy(self):
        assert "churches" in self.sql

    def test_sermons_keeps_a_public_read_policy(self):
        assert "sermons" in self.sql

    def test_site_config_never_gets_a_public_read(self):
        """site_config holds connector secrets — grok_api_key,
        ms365_client_secret, gloo_client_secret. It must never be USING (true).
        """
        for statement in policy_statements(capture_sql(load_migration())):
            if "site_config" in statement.lower():
                assert not re.search(r"USING\s*\(\s*true\s*\)", statement, re.I), (
                    f"site_config policy is publicly readable:\n{statement}"
                )


# ---------------------------------------------------------------------------
# Downgrade
# ---------------------------------------------------------------------------

class TestDowngrade:
    def test_downgrade_drops_what_it_created(self):
        sql = "\n".join(capture_sql(load_migration(), "downgrade")).upper()
        assert "DROP POLICY" in sql
        assert "DROP FUNCTION" in sql
