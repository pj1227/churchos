"""
test_keepalive_workflow.py — TDD contract tests for the Supabase keepalive workflow.

Supabase pauses free-tier projects after 7 consecutive days with no API traffic.
`.github/workflows/supabase-keepalive.yml` prevents that by pinging PostgREST on
a schedule. These tests are the contract for that workflow.

Why they live here rather than in a CI-config directory: pytest already runs in CI
(see .github/workflows/ci.yml → pytest job), so this is the cheapest place to get
the assertions executed on every PR. Nothing here touches a database or network —
the workflow YAML is parsed off disk.

The security assertions are the point. A keepalive workflow is a standing,
scheduled credential use; if it ever starts carrying the Supabase secret key, that
key is exposed to every workflow-write path in the repo. These tests fail loudly
if that happens.

How it connects:
  - Reads .github/workflows/supabase-keepalive.yml from the repo root
  - Mirrors the contract-test style of tests/test_rls_migration.py
"""
import re
from pathlib import Path

import pytest

yaml = pytest.importorskip("yaml", reason="PyYAML required for workflow contract tests")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[3]
WORKFLOW_PATH = REPO_ROOT / ".github" / "workflows" / "supabase-keepalive.yml"

# Supabase pauses at 7 days. Anything slower than this leaves no room for a
# single failed run.
MAX_ALLOWED_INTERVAL_DAYS = 3


def load_workflow() -> dict:
    """Parse the keepalive workflow YAML."""
    return yaml.safe_load(WORKFLOW_PATH.read_text(encoding="utf-8"))


def workflow_text() -> str:
    return WORKFLOW_PATH.read_text(encoding="utf-8")


def triggers(wf: dict) -> dict:
    """Return the `on:` block.

    PyYAML resolves an unquoted `on` key to the boolean True (YAML 1.1), so the
    key may be either `"on"` or `True` depending on how it was written.
    """
    return wf.get("on", wf.get(True, {}))


# ---------------------------------------------------------------------------
# Existence
# ---------------------------------------------------------------------------

class TestWorkflowExists:
    def test_workflow_file_exists(self):
        assert WORKFLOW_PATH.exists(), (
            f"Workflow not found: {WORKFLOW_PATH}\n"
            "Create .github/workflows/supabase-keepalive.yml"
        )

    def test_workflow_is_valid_yaml(self):
        wf = load_workflow()
        assert isinstance(wf, dict), "Workflow did not parse to a mapping"

    def test_workflow_has_a_name(self):
        assert load_workflow().get("name")


# ---------------------------------------------------------------------------
# Schedule
# ---------------------------------------------------------------------------

class TestSchedule:
    def setup_method(self):
        self.on = triggers(load_workflow())

    def test_has_schedule_trigger(self):
        assert "schedule" in self.on, "Workflow must run on a cron schedule"

    def test_has_manual_dispatch_escape_hatch(self):
        """GitHub disables cron on repos with no commits for 60 days.

        workflow_dispatch lets the project be un-paused by hand without editing
        the workflow first.
        """
        assert "workflow_dispatch" in self.on

    def test_cron_runs_at_least_every_three_days(self):
        crons = [entry["cron"] for entry in self.on["schedule"]]
        assert crons, "schedule: block has no cron entries"

        day_of_month = crons[0].split()[2]

        if day_of_month == "*":
            interval = 1  # daily
        else:
            match = re.fullmatch(r"\*/(\d+)", day_of_month)
            assert match, (
                f"Unrecognized day-of-month field {day_of_month!r}; "
                "expected '*' or a '*/N' step."
            )
            interval = int(match.group(1))

        assert interval <= MAX_ALLOWED_INTERVAL_DAYS, (
            f"Cron runs every {interval} days. Supabase pauses at 7 days, so a "
            f"single failed run must not be enough to reach the limit. "
            f"Use an interval of {MAX_ALLOWED_INTERVAL_DAYS} days or less."
        )


# ---------------------------------------------------------------------------
# Security — the reason these tests exist
# ---------------------------------------------------------------------------

class TestCredentialHandling:
    def setup_method(self):
        self.text = workflow_text()

    def test_never_references_the_service_key(self):
        """The secret key bypasses RLS. A keepalive ping needs no such power."""
        forbidden = ("SUPABASE_SERVICE_KEY", "SUPABASE_SERVICE_ROLE", "SERVICE_ROLE_KEY")
        for name in forbidden:
            assert name not in self.text, (
                f"{name} appears in the keepalive workflow. Use the anon/publishable "
                "key — a scheduled ping must never carry an RLS-bypassing credential."
            )

    def test_uses_the_anon_key(self):
        assert "SUPABASE_ANON_KEY" in self.text

    def test_credentials_come_from_secrets_not_literals(self):
        """Every Supabase env value must be a ${{ secrets.* }} reference."""
        wf = load_workflow()
        job = next(iter(wf["jobs"].values()))
        env_values = list(job.get("env", {}).values())
        for step in job.get("steps", []):
            env_values.extend(step.get("env", {}).values())

        assert env_values, "Workflow defines no env values to check"
        for value in env_values:
            assert "secrets." in str(value), (
                f"Hardcoded credential in workflow env: {value!r}"
            )

    def test_no_literal_jwt_in_source(self):
        """Supabase keys are JWTs — catch one accidentally pasted in."""
        assert not re.search(r"eyJ[A-Za-z0-9_-]{10,}", self.text), (
            "A literal JWT appears in the workflow. Move it to a repo secret."
        )


# ---------------------------------------------------------------------------
# Failure behaviour
# ---------------------------------------------------------------------------

class TestFailsLoudly:
    def setup_method(self):
        self.text = workflow_text()

    def test_curl_fails_on_http_error(self):
        """Without --fail, curl exits 0 on a 401 and the workflow reports success
        while the project quietly drifts toward a pause."""
        assert "--fail" in self.text or re.search(r"curl\s+-[a-zA-Z]*f", self.text), (
            "curl must use --fail so an HTTP error fails the job."
        )

    def test_targets_the_rest_api(self):
        assert "/rest/v1/" in self.text

    def test_ping_target_is_readable_with_the_anon_key(self):
        """The ping must target a table anon can actually SELECT.

        `churches` and `sermons` look like the obvious targets — both have a
        `public read USING (true)` policy — but both return HTTP 500 to anon:

            42P17 infinite recursion detected in policy for relation "profiles"

        Their write policies are `FOR ALL`, so the USING clause is evaluated on
        SELECT too, and it selects from public.profiles, whose own
        "admin can read all" policy selects from public.profiles. Combined with
        `curl --fail`, either target would fail the job on every run.

        This allowlist is what has been verified to return 200 with the
        publishable key. Add to it only after re-checking against the live
        project; the recursion fix is tracked separately.
        """
        anon_readable = {"church_events", "pages", "announcements", "prayer_requests"}

        match = re.search(r"/rest/v1/([a-z_]+)", self.text)
        assert match, "Could not find the PostgREST table in the ping URL"
        table = match.group(1)

        assert table in anon_readable, (
            f"Ping targets {table!r}, which is not known to be anon-readable. "
            f"Verified targets: {sorted(anon_readable)}. "
            "If you meant to add one, confirm it returns 200 with the "
            "publishable key first — with --fail, an unreadable target fails "
            "the job on every scheduled run."
        )
