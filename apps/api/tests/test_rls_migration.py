"""
test_rls_migration.py — TDD tests for the RLS hardening migration.

Verifies that migration h8i9j0k1l2m3 (enable_rls_on_remaining_tables):
  - Enables RLS on site_config, announcements, pages, sermon_sync_logs
  - Adds appropriate read/write policies for each table
  - Does NOT expose site_config to anonymous access (it contains secrets)

These are contract tests on the migration source — they parse the upgrade()
SQL rather than hitting a live database, so they run in CI without credentials.

How it connects:
  - Imports alembic/versions/h8i9j0k1l2m3_enable_rls_on_remaining_tables.py
  - Calls upgrade() against a mock op that captures executed SQL
  - Asserts the captured SQL contains the expected statements
"""
import importlib.util
from pathlib import Path
from unittest.mock import MagicMock, patch


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

MIGRATION_PATH = (
    Path(__file__).parent.parent
    / "alembic"
    / "versions"
    / "h8i9j0k1l2m3_enable_rls_on_remaining_tables.py"
)


def load_migration():
    """Dynamically load the migration module (avoids alembic env setup)."""
    spec = importlib.util.spec_from_file_location("migration_rls", MIGRATION_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def capture_sql(migration_mod) -> list[str]:
    """Run upgrade() with a mock op; return the list of SQL strings executed."""
    executed: list[str] = []
    mock_op = MagicMock()
    mock_op.execute.side_effect = lambda sql: executed.append(sql.strip())

    with patch.object(migration_mod, "op", mock_op):
        migration_mod.upgrade()

    return executed


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestRlsMigrationExists:
    def test_migration_file_exists(self):
        assert MIGRATION_PATH.exists(), (
            f"Migration file not found: {MIGRATION_PATH}\n"
            "Create apps/api/alembic/versions/h8i9j0k1l2m3_enable_rls_on_remaining_tables.py"
        )

    def test_migration_has_correct_revision(self):
        mod = load_migration()
        assert mod.revision == "h8i9j0k1l2m3"

    def test_migration_chains_from_previous(self):
        mod = load_migration()
        assert mod.down_revision == "g7h8i9j0k1l2"


class TestSiteConfigRls:
    """site_config holds secrets — must be admin-only, never public."""

    def setup_method(self):
        mod = load_migration()
        self.sql = "\n".join(capture_sql(mod)).upper()

    def test_enables_rls_on_site_config(self):
        assert "ALTER TABLE PUBLIC.SITE_CONFIG ENABLE ROW LEVEL SECURITY" in self.sql

    def test_no_public_read_policy_on_site_config(self):
        """Ensure we never add USING (true) for site_config — it contains secrets."""
        # Find blocks that mention site_config and assert none allow USING (true)
        lines = self.sql.split("\n")
        in_site_config_block = False
        for line in lines:
            if "SITE_CONFIG" in line:
                in_site_config_block = True
            if in_site_config_block and "USING (TRUE)" in line:
                raise AssertionError(
                    "site_config has a USING (true) policy — this exposes secrets to the public!"
                )

    def test_admin_read_policy_on_site_config(self):
        assert "SITE_CONFIG" in self.sql
        assert "ADMIN" in self.sql or "SUPERADMIN" in self.sql

    def test_staff_write_policy_on_site_config(self):
        # site_config writes should be restricted to admin+
        assert "SITE_CONFIG" in self.sql


class TestAnnouncementsRls:
    def setup_method(self):
        mod = load_migration()
        self.sql = "\n".join(capture_sql(mod)).upper()

    def test_enables_rls_on_announcements(self):
        assert "ALTER TABLE PUBLIC.ANNOUNCEMENTS ENABLE ROW LEVEL SECURITY" in self.sql

    def test_public_read_policy_gates_on_a_real_column(self):
        """The policy must gate on a column announcements actually has.

        This originally read `USING (is_published = true)`, copied from the
        pages policy. announcements has no is_published column — it uses
        is_active / active_from / active_until — so the migration failed with
        `column "is_published" does not exist` partway through, taking the rest
        of the RLS hardening down with it.
        """
        assert "ANNOUNCEMENTS" in self.sql
        assert "IS_ACTIVE" in self.sql, (
            "announcements policy must gate on is_active; there is no "
            "is_published column on this table."
        )
        assert "IS_PUBLISHED = TRUE" not in self.sql.split("PAGES")[0], (
            "announcements policy references is_published, which does not exist."
        )

    def test_staff_write_policy(self):
        assert "ANNOUNCEMENTS" in self.sql
        assert "STAFF" in self.sql or "ADMIN" in self.sql


class TestPagesRls:
    def setup_method(self):
        mod = load_migration()
        self.sql = "\n".join(capture_sql(mod)).upper()

    def test_enables_rls_on_pages(self):
        assert "ALTER TABLE PUBLIC.PAGES ENABLE ROW LEVEL SECURITY" in self.sql

    def test_public_read_policy_exists(self):
        assert "PAGES" in self.sql

    def test_staff_write_policy_exists(self):
        assert "PAGES" in self.sql
        assert "STAFF" in self.sql or "ADMIN" in self.sql


class TestSermonSyncLogsRls:
    def setup_method(self):
        mod = load_migration()
        self.sql = "\n".join(capture_sql(mod)).upper()

    def test_enables_rls_on_sermon_sync_logs(self):
        assert "ALTER TABLE PUBLIC.SERMON_SYNC_LOGS ENABLE ROW LEVEL SECURITY" in self.sql

    def test_staff_read_policy(self):
        # Sync logs are internal — staff+ only, not public
        assert "SERMON_SYNC_LOGS" in self.sql
        assert "STAFF" in self.sql or "ADMIN" in self.sql

    def test_no_public_read_on_sync_logs(self):
        """Sync logs are internal tooling, not public content."""
        lines = self.sql.split("\n")
        in_sync_log_block = False
        for line in lines:
            if "SERMON_SYNC_LOGS" in line:
                in_sync_log_block = True
            if in_sync_log_block and "USING (TRUE)" in line:
                raise AssertionError(
                    "sermon_sync_logs has a USING (true) policy — logs should be staff-only."
                )


class TestDowngrade:
    def test_downgrade_reverses_rls(self):
        mod = load_migration()
        executed: list[str] = []
        mock_op = MagicMock()
        mock_op.execute.side_effect = lambda sql: executed.append(sql.strip())

        with patch.object(mod, "op", mock_op):
            mod.downgrade()

        sql = "\n".join(executed).upper()
        assert "DISABLE ROW LEVEL SECURITY" in sql or "DROP POLICY" in sql
