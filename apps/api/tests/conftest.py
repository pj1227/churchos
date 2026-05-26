"""
conftest.py — pytest fixtures shared across all API tests.

Exists at this layer because pytest discovers it automatically for the entire
tests/ directory. The `client` fixture gives every test a fresh HTTPX
TestClient bound to our FastAPI app without spinning up a real server.

JWT secret handling:
  `settings = Settings()` is a module-level singleton created the moment
  app/config.py is imported. If SUPABASE_JWT_SECRET is already present in
  the shell environment (from .env, .bashrc, etc.), os.environ.setdefault
  would leave the real value in place, causing token verification to fail
  with the test secret.

  To keep tests hermetic we directly overwrite settings.supabase_jwt_secret
  after import. This is safe because pydantic-settings models are mutable
  by default (frozen=False). All code that reads the secret does so via
  the settings object at call time, not at import time, so the override
  takes effect for every test in the session.

  The value here must match TEST_JWT_SECRET in test_auth.py — both sides
  of the HS256 verification use the same dummy secret so no real Supabase
  credentials are needed in CI.
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.config import settings

# Force all Supabase credentials to test values regardless of what the
# shell environment or .env file contains. This keeps every test hermetic —
# no real Supabase project is contacted during the test suite.
TEST_JWT_SECRET = "test-jwt-secret-for-pytest-only-32chars!!"
settings.supabase_jwt_secret = TEST_JWT_SECRET
settings.supabase_url = "https://test.supabase.co"
settings.supabase_service_key = "test-service-role-key"


@pytest.fixture
def client() -> TestClient:
    """Return a synchronous HTTPX test client for the FastAPI app."""
    return TestClient(app)
