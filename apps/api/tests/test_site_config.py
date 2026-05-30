"""
test_site_config.py — TDD tests for the site configuration API.

Endpoints under test:
  GET    /site-config          staff+   — list all config keys (secrets masked)
  GET    /site-config/{key}    staff+   — get a single value
  PUT    /site-config/{key}    admin+   — upsert a key/value pair

Security contracts:
  - All endpoints require staff role minimum
  - is_secret=true values are masked ("***") in GET responses
  - Only admin+ can write config values
"""

import time
import uuid
from unittest.mock import patch

import jwt
from fastapi.testclient import TestClient

TEST_JWT_SECRET = "test-jwt-secret-for-pytest-only-32chars!!"
USER_ID_STAFF   = str(uuid.uuid4())
USER_ID_ADMIN   = str(uuid.uuid4())
USER_ID_MEMBER  = str(uuid.uuid4())

MOCK_CONFIG = [
    {
        "id":         1,
        "church_id":  "default",
        "key":        "prayer_chain_email",
        "value":      "prayer@libbynaz.org",
        "is_secret":  False,
        "is_json":    False,
        "updated_at": "2026-05-29T10:00:00Z",
    },
    {
        "id":         2,
        "church_id":  "default",
        "key":        "smtp_password",
        "value":      "supersecret",
        "is_secret":  True,
        "is_json":    False,
        "updated_at": "2026-05-29T10:00:00Z",
    },
]

MOCK_EMAIL_CONFIG = MOCK_CONFIG[0]


def make_token(user_id: str, expires_in: int = 3600) -> str:
    now = int(time.time())
    return jwt.encode(
        {"sub": user_id, "role": "authenticated", "iat": now, "exp": now + expires_in},
        TEST_JWT_SECRET, algorithm="HS256",
    )


def auth_header(user_id: str) -> dict:
    return {"Authorization": f"Bearer {make_token(user_id)}"}


def mock_profile(user_id: str, role: str) -> dict:
    return {"id": user_id, "role": role, "church_id": "default",
            "church_slug": "libby-naz", "email": f"{role}@test.com", "display_name": None}


# ---------------------------------------------------------------------------
# GET /site-config
# ---------------------------------------------------------------------------
class TestListSiteConfig:
    def test_unauthenticated_returns_401(self, client: TestClient):
        assert client.get("/site-config").status_code == 401

    def test_member_returns_403(self, client: TestClient):
        with patch("app.dependencies.auth.get_profile",
                   return_value=mock_profile(USER_ID_MEMBER, "member")):
            r = client.get("/site-config", headers=auth_header(USER_ID_MEMBER))
        assert r.status_code == 403

    def test_staff_can_list_config(self, client: TestClient):
        with patch("app.dependencies.auth.get_profile",
                   return_value=mock_profile(USER_ID_STAFF, "staff")), \
             patch("app.crud.site_config.list_config", return_value=MOCK_CONFIG):
            r = client.get("/site-config", headers=auth_header(USER_ID_STAFF))
        assert r.status_code == 200
        assert len(r.json()) == 2

    def test_secret_values_are_masked(self, client: TestClient):
        with patch("app.dependencies.auth.get_profile",
                   return_value=mock_profile(USER_ID_STAFF, "staff")), \
             patch("app.crud.site_config.list_config", return_value=MOCK_CONFIG):
            r = client.get("/site-config", headers=auth_header(USER_ID_STAFF))
        items = {item["key"]: item for item in r.json()}
        assert items["smtp_password"]["value"] == "***"
        assert items["prayer_chain_email"]["value"] == "prayer@libbynaz.org"


# ---------------------------------------------------------------------------
# GET /site-config/{key}
# ---------------------------------------------------------------------------
class TestGetSiteConfigKey:
    def test_unauthenticated_returns_401(self, client: TestClient):
        assert client.get("/site-config/prayer_chain_email").status_code == 401

    def test_staff_can_get_key(self, client: TestClient):
        with patch("app.dependencies.auth.get_profile",
                   return_value=mock_profile(USER_ID_STAFF, "staff")), \
             patch("app.crud.site_config.get_config_value",
                   return_value=MOCK_EMAIL_CONFIG):
            r = client.get("/site-config/prayer_chain_email",
                           headers=auth_header(USER_ID_STAFF))
        assert r.status_code == 200
        assert r.json()["value"] == "prayer@libbynaz.org"

    def test_missing_key_returns_404(self, client: TestClient):
        with patch("app.dependencies.auth.get_profile",
                   return_value=mock_profile(USER_ID_STAFF, "staff")), \
             patch("app.crud.site_config.get_config_value", return_value=None):
            r = client.get("/site-config/nonexistent",
                           headers=auth_header(USER_ID_STAFF))
        assert r.status_code == 404


# ---------------------------------------------------------------------------
# PUT /site-config/{key}
# ---------------------------------------------------------------------------
class TestSetSiteConfigKey:
    def test_unauthenticated_returns_401(self, client: TestClient):
        assert client.put("/site-config/prayer_chain_email",
                          json={"value": "new@test.com"}).status_code == 401

    def test_staff_cannot_write(self, client: TestClient):
        with patch("app.dependencies.auth.get_profile",
                   return_value=mock_profile(USER_ID_STAFF, "staff")):
            r = client.put("/site-config/prayer_chain_email",
                           json={"value": "new@test.com"},
                           headers=auth_header(USER_ID_STAFF))
        assert r.status_code == 403

    def test_admin_can_write(self, client: TestClient):
        updated = {**MOCK_EMAIL_CONFIG, "value": "new@libbynaz.org"}
        with patch("app.dependencies.auth.get_profile",
                   return_value=mock_profile(USER_ID_ADMIN, "admin")), \
             patch("app.crud.site_config.set_config_value", return_value=updated):
            r = client.put("/site-config/prayer_chain_email",
                           json={"value": "new@libbynaz.org"},
                           headers=auth_header(USER_ID_ADMIN))
        assert r.status_code == 200
        assert r.json()["value"] == "new@libbynaz.org"

    def test_value_is_required(self, client: TestClient):
        with patch("app.dependencies.auth.get_profile",
                   return_value=mock_profile(USER_ID_ADMIN, "admin")):
            r = client.put("/site-config/prayer_chain_email",
                           json={},
                           headers=auth_header(USER_ID_ADMIN))
        assert r.status_code == 422
