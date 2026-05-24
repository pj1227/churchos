"""
test_get_profile.py — Unit tests for the get_profile function.

These tests are written BEFORE the real implementation. They will fail
because get_profile currently returns None (stub) and does not import httpx.

What we are testing:
  get_profile(user_id) — fetches a row from public.profiles via the
  Supabase REST API using the service role key (bypasses RLS).

Test strategy:
  We mock httpx.get so these tests never hit a real network. The mock
  verifies that:
    1. get_profile returns a dict when Supabase returns a matching row
    2. get_profile returns None when Supabase returns an empty list
    3. get_profile passes the correct Authorization header (service role key)

Why httpx and not supabase-py:
  httpx is already in requirements.txt. A direct REST call to the
  Supabase PostgREST endpoint is explicit, easy to mock, and avoids
  adding another dependency. The supabase-py client adds value in Phase 4
  when we need realtime subscriptions — for a single SELECT it's overkill.

How it connects:
  - app/dependencies/auth.py: get_profile will import and call httpx.get
  - app/config.py: settings.supabase_url + settings.supabase_service_key
    supply the endpoint and auth header
  - tests/conftest.py: sets test values for both config fields
"""
from unittest.mock import MagicMock, patch

import pytest

from app.dependencies.auth import get_profile

TEST_USER_ID = "550e8400-e29b-41d4-a716-446655440000"

SUPABASE_PROFILE_ROW = {
    "id": TEST_USER_ID,
    "email": "test@libbynaz.org",
    "display_name": None,
    "role": "member",
    "church_slug": "libby-naz",
}


def _mock_response(rows: list) -> MagicMock:
    """Build a mock httpx.Response that returns `rows` from .json()."""
    resp = MagicMock()
    resp.json.return_value = rows
    resp.raise_for_status.return_value = None
    return resp


class TestGetProfile:
    def test_returns_profile_dict_when_found(self):
        """Supabase returns one row → get_profile returns that dict."""
        with patch("app.dependencies.auth.httpx.get", return_value=_mock_response([SUPABASE_PROFILE_ROW])):
            result = get_profile(TEST_USER_ID)

        assert result is not None
        assert result["id"] == TEST_USER_ID
        assert result["email"] == "test@libbynaz.org"
        assert result["role"] == "member"
        assert result["church_slug"] == "libby-naz"

    def test_returns_none_when_not_found(self):
        """Supabase returns empty list → get_profile returns None."""
        with patch("app.dependencies.auth.httpx.get", return_value=_mock_response([])):
            result = get_profile(TEST_USER_ID)

        assert result is None

    def test_uses_service_role_authorization_header(self):
        """
        The request must use the service role key, not the anon key.
        Service role bypasses RLS — critical so the API can read any profile
        regardless of the caller's JWT.
        """
        mock_get = MagicMock(return_value=_mock_response([SUPABASE_PROFILE_ROW]))

        with patch("app.dependencies.auth.httpx.get", mock_get):
            get_profile(TEST_USER_ID)

        _, kwargs = mock_get.call_args
        auth_header = kwargs["headers"]["Authorization"]
        assert auth_header.startswith("Bearer "), (
            "Authorization header must be 'Bearer <service_role_key>'"
        )
