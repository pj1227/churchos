"""
test_sermons.py — TDD tests for the sermon CRUD API.

Written against the real public.sermons schema (Logos-synced, varchar IDs,
church_id FK). Tests will fail with 404 until the router is registered in
main.py — that is the expected TDD starting state.

Endpoints under test:
  GET    /sermons          public   — paginated list
  GET    /sermons/{id}     public   — single sermon or 404
  POST   /sermons          staff+   — manual sermon creation
  PATCH  /sermons/{id}     staff+   — partial update of editable fields
  DELETE /sermons/{id}     admin+   — hard delete

RBAC contract:
  unauthenticated          → POST/PATCH/DELETE → 401
  member                   → POST/PATCH/DELETE → 403
  staff                    → POST/PATCH allowed, DELETE → 403
  admin / superadmin       → full access

How it connects:
  - conftest.py supplies the `client` fixture and overrides JWT secret
  - app.crud.sermons is patched so no database is needed in CI
  - app.dependencies.auth.get_profile is patched to return a mock profile
"""

import time
import uuid
from unittest.mock import patch

import jwt
from fastapi.testclient import TestClient

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
TEST_JWT_SECRET = "test-jwt-secret-for-pytest-only-32chars!!"
TEST_CHURCH_ID  = "church-0000-0000-0000-000000000001"
USER_ID_STAFF   = str(uuid.uuid4())
USER_ID_ADMIN   = str(uuid.uuid4())
USER_ID_MEMBER  = str(uuid.uuid4())

MOCK_SERMON = {
    "id":                   "sermon-0000-0000-0000-000000000001",
    "church_id":            TEST_CHURCH_ID,
    "logos_id":             "logos-abc123",
    "logos_url":            "https://logos.com/sermons/abc123",
    "logos_embed_url":      None,
    "logos_series_id":      None,
    "title":                "Grace Abounding",
    "speaker_name":         "Pastor John",
    "series":               "Romans",
    "date":                 "2026-05-25",
    "description":          "A deep look at Romans 5.",
    "notes":                None,
    "scripture_reference":  "Romans 5:1-11",
    "thumbnail_url":        None,
    "series_thumbnail_url": None,
    "duration_seconds":     2700,
    "tags":                 "grace,faith",
    "has_audio":            True,
    "has_video":            False,
    "has_slides":           False,
    "is_published":         True,
    "logos_published_at":   "2026-05-25T10:00:00Z",
    "logos_updated_at":     "2026-05-25T10:00:00Z",
    "first_synced_at":      "2026-05-25T10:00:00Z",
    "last_synced_at":       "2026-05-25T10:00:00Z",
    "created_at":           "2026-05-25T10:00:00Z",
    "updated_at":           "2026-05-25T10:00:00Z",
}

CREATE_PAYLOAD = {
    "title":       "Grace Abounding",
    "speaker_name": "Pastor John",
    "date":        "2026-05-25",
}

UPDATE_PAYLOAD = {
    "description": "Updated description.",
    "is_published": False,
}


# ---------------------------------------------------------------------------
# JWT helpers
# ---------------------------------------------------------------------------
def make_token(user_id: str, role: str, expires_in: int = 3600) -> str:
    now = int(time.time())
    return jwt.encode(
        {"sub": user_id, "role": "authenticated", "iat": now, "exp": now + expires_in},
        TEST_JWT_SECRET,
        algorithm="HS256",
    )


def auth_header(role: str, user_id: str | None = None) -> dict:
    uid = user_id or str(uuid.uuid4())
    return {"Authorization": f"Bearer {make_token(uid, role)}"}


def mock_profile(user_id: str, role: str) -> dict:
    return {"id": user_id, "role": role, "church_id": TEST_CHURCH_ID,
            "church_slug": "libby-naz", "email": f"{role}@test.com",
            "display_name": None}


# ---------------------------------------------------------------------------
# GET /sermons — public
# ---------------------------------------------------------------------------
class TestListSermons:
    def test_returns_200_with_list(self, client: TestClient):
        with patch("app.crud.sermons.list_sermons", return_value=[MOCK_SERMON]):
            r = client.get("/sermons")
        assert r.status_code == 200
        assert r.json()[0]["title"] == "Grace Abounding"

    def test_returns_empty_list(self, client: TestClient):
        with patch("app.crud.sermons.list_sermons", return_value=[]):
            r = client.get("/sermons")
        assert r.status_code == 200
        assert r.json() == []

    def test_no_auth_required(self, client: TestClient):
        with patch("app.crud.sermons.list_sermons", return_value=[MOCK_SERMON]):
            r = client.get("/sermons")
        assert r.status_code == 200


# ---------------------------------------------------------------------------
# GET /sermons/{id} — public
# ---------------------------------------------------------------------------
class TestGetSermon:
    def test_returns_200(self, client: TestClient):
        with patch("app.crud.sermons.get_sermon", return_value=MOCK_SERMON):
            r = client.get(f"/sermons/{MOCK_SERMON['id']}")
        assert r.status_code == 200
        assert r.json()["id"] == MOCK_SERMON["id"]

    def test_returns_404_when_missing(self, client: TestClient):
        with patch("app.crud.sermons.get_sermon", return_value=None):
            r = client.get("/sermons/does-not-exist")
        assert r.status_code == 404


# ---------------------------------------------------------------------------
# POST /sermons — staff+
# ---------------------------------------------------------------------------
class TestCreateSermon:
    def test_unauthenticated_returns_401(self, client: TestClient):
        assert client.post("/sermons", json=CREATE_PAYLOAD).status_code == 401

    def test_member_returns_403(self, client: TestClient):
        with patch("app.dependencies.auth.get_profile",
                   return_value=mock_profile(USER_ID_MEMBER, "member")):
            r = client.post("/sermons", json=CREATE_PAYLOAD,
                            headers=auth_header("member", USER_ID_MEMBER))
        assert r.status_code == 403

    def test_staff_can_create(self, client: TestClient):
        with patch("app.dependencies.auth.get_profile",
                   return_value=mock_profile(USER_ID_STAFF, "staff")), \
             patch("app.crud.sermons.create_sermon", return_value=MOCK_SERMON):
            r = client.post("/sermons", json=CREATE_PAYLOAD,
                            headers=auth_header("staff", USER_ID_STAFF))
        assert r.status_code == 201
        assert r.json()["title"] == "Grace Abounding"

    def test_admin_can_create(self, client: TestClient):
        with patch("app.dependencies.auth.get_profile",
                   return_value=mock_profile(USER_ID_ADMIN, "admin")), \
             patch("app.crud.sermons.create_sermon", return_value=MOCK_SERMON):
            r = client.post("/sermons", json=CREATE_PAYLOAD,
                            headers=auth_header("admin", USER_ID_ADMIN))
        assert r.status_code == 201

    def test_missing_title_returns_422(self, client: TestClient):
        with patch("app.dependencies.auth.get_profile",
                   return_value=mock_profile(USER_ID_STAFF, "staff")):
            r = client.post("/sermons",
                            json={"speaker_name": "Pastor John", "date": "2026-05-25"},
                            headers=auth_header("staff", USER_ID_STAFF))
        assert r.status_code == 422


# ---------------------------------------------------------------------------
# PATCH /sermons/{id} — staff+
# ---------------------------------------------------------------------------
class TestUpdateSermon:
    def test_unauthenticated_returns_401(self, client: TestClient):
        assert client.patch(f"/sermons/{MOCK_SERMON['id']}",
                            json=UPDATE_PAYLOAD).status_code == 401

    def test_member_returns_403(self, client: TestClient):
        with patch("app.dependencies.auth.get_profile",
                   return_value=mock_profile(USER_ID_MEMBER, "member")):
            r = client.patch(f"/sermons/{MOCK_SERMON['id']}", json=UPDATE_PAYLOAD,
                             headers=auth_header("member", USER_ID_MEMBER))
        assert r.status_code == 403

    def test_staff_can_update(self, client: TestClient):
        updated = {**MOCK_SERMON, "description": "Updated description.", "is_published": False}
        with patch("app.dependencies.auth.get_profile",
                   return_value=mock_profile(USER_ID_STAFF, "staff")), \
             patch("app.crud.sermons.get_sermon", return_value=MOCK_SERMON), \
             patch("app.crud.sermons.update_sermon", return_value=updated):
            r = client.patch(f"/sermons/{MOCK_SERMON['id']}", json=UPDATE_PAYLOAD,
                             headers=auth_header("staff", USER_ID_STAFF))
        assert r.status_code == 200
        assert r.json()["is_published"] is False

    def test_patch_nonexistent_returns_404(self, client: TestClient):
        with patch("app.dependencies.auth.get_profile",
                   return_value=mock_profile(USER_ID_STAFF, "staff")), \
             patch("app.crud.sermons.get_sermon", return_value=None):
            r = client.patch("/sermons/does-not-exist", json=UPDATE_PAYLOAD,
                             headers=auth_header("staff", USER_ID_STAFF))
        assert r.status_code == 404


# ---------------------------------------------------------------------------
# DELETE /sermons/{id} — admin+
# ---------------------------------------------------------------------------
class TestDeleteSermon:
    def test_unauthenticated_returns_401(self, client: TestClient):
        assert client.delete(f"/sermons/{MOCK_SERMON['id']}").status_code == 401

    def test_staff_cannot_delete(self, client: TestClient):
        """Staff can write but NOT delete — admin+ only."""
        with patch("app.dependencies.auth.get_profile",
                   return_value=mock_profile(USER_ID_STAFF, "staff")):
            r = client.delete(f"/sermons/{MOCK_SERMON['id']}",
                              headers=auth_header("staff", USER_ID_STAFF))
        assert r.status_code == 403

    def test_admin_can_delete(self, client: TestClient):
        with patch("app.dependencies.auth.get_profile",
                   return_value=mock_profile(USER_ID_ADMIN, "admin")), \
             patch("app.crud.sermons.get_sermon", return_value=MOCK_SERMON), \
             patch("app.crud.sermons.delete_sermon", return_value=None):
            r = client.delete(f"/sermons/{MOCK_SERMON['id']}",
                              headers=auth_header("admin", USER_ID_ADMIN))
        assert r.status_code == 204

    def test_delete_nonexistent_returns_404(self, client: TestClient):
        with patch("app.dependencies.auth.get_profile",
                   return_value=mock_profile(USER_ID_ADMIN, "admin")), \
             patch("app.crud.sermons.get_sermon", return_value=None):
            r = client.delete("/sermons/does-not-exist",
                              headers=auth_header("admin", USER_ID_ADMIN))
        assert r.status_code == 404
