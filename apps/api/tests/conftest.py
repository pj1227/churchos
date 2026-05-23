"""
conftest.py — pytest fixtures shared across all API tests.

Exists at this layer because pytest discovers it automatically for the entire
tests/ directory. The `client` fixture gives every test a fresh HTTPX
TestClient bound to our FastAPI app without spinning up a real server.
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client() -> TestClient:
    """Return a synchronous HTTPX test client for the FastAPI app."""
    return TestClient(app)
