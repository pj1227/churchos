"""
test_events.py — TDD tests for the church_events CRUD API.

Written against the real public.church_events schema. Tests will fail with
404 until the router is registered in main.py — expected TDD starting state.

Endpoints under test:
  GET    /events          public   — paginated list
  GET    /events/{id}     public   — single event or 404
  POST   /events          staff+   — create event
  PATCH  /events/{id}     staff+   — partial update
  DELETE /events/{id}     admin+   — hard delete

RBAC contract:
  unauthenticated          → POST/PATCH/DELETE → 401
  member                   → POST/PATCH/DELETE → 403
  staff                    → POST/PATCH allowed, DELETE → 403
  admin / superadmin       → full access
"""

import time
import uuid
from unittest.mock import patch

import jwt
import pytest
from fastapi.testclient import TestClient

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
TEST_JWT_SECRET = "test-jwt-secret-for-pytest-only-32chars!!"
TEST_CHURCH_ID  = "church-0000-0000-0000-000000000001"
USER_ID_STAFF   = str(uuid.uuid4())
USER_ID_ADMIN   = str(uuid.uuid4())
USER_ID_MEMBER  = str(uuid.uuid4())

MOCK_EVENT = {
    "id":                    "event-0000-0000-0000-000000000001",
    "church_id":             TEST_CHURCH_ID,
    "title":                 "Sunday Service",
    "description":           "Weekly worship gathering.",
    "start_at":              "2026-06-01T10:00:00+00:00",
    "end_at":                "2026-06-01T11:30:00+00:00",
    "all_day":               False,
    "location":              "Main Sanctuary",
    "is_virtual":            False,
    "virtual_url":           None,
    "category":              "worship",
    "recurrence":            "weekly",
    "image_url":             None,
    "registration_required": False,
    "registration_url":      None,
    "created_by":            USER_ID_STAFF,
    "is_published":          True,
    "created_at":            "2026-05-27T10:00:00Z",
    "updated_at":            "2026-05-27T10:00:00Z",
}

CREATE_PAYLOAD = {
    "title":    "Sunday Service",
    "start_at": "2026-06-01T10:00:00+00:00",
    "end_at":   "2026-06-01T11:30:00+00:00",
}

UPDATE_PAYLOAD = {
    "description": "Updated description.",
    "is_published": True,
}


# ---------------------------------------------------------------------------
# JWT helpers (same pattern as test_sermons.py)
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
# GET /events — public
# ---------------------------------------------------------------------------
class TestListEvents:
    def test_returns_200_with_list(self, client: TestClient):
        with patch("app.crud.events.list_events", return_value=[MOCK_EVENT]):
            r = client.get("/events")
        assert r.status_code == 200
        assert r.json()[0]["title"] == "Sunday Service"

    def test_returns_empty_list(self, client: TestClient):
        with patch("app.crud.events.list_events", return_value=[]):
            r = client.get("/events")
        assert r.status_code == 200
        assert r.json() == []

    def test_no_auth_required(self, client: TestClient):
        with patch("app.crud.events.list_events", return_value=[MOCK_EVENT]):
            r = client.get("/events")
        assert r.status_code == 200


# ---------------------------------------------------------------------------
# GET /events/{id} — public
# ---------------------------------------------------------------------------
class TestGetEvent:
    def test_returns_200(self, client: TestClient):
        with patch("app.crud.events.get_event", return_value=MOCK_EVENT):
            r = client.get(f"/events/{MOCK_EVENT['id']}")
        assert r.status_code == 200
        assert r.json()["id"] == MOCK_EVENT["id"]

    def test_returns_404_when_missing(self, client: TestClient):
        with patch("app.crud.events.get_event", return_value=None):
            r = client.get("/events/does-not-exist")
        assert r.status_code == 404


# ---------------------------------------------------------------------------
# POST /events — staff+
# ---------------------------------------------------------------------------
class TestCreateEvent:
    def test_unauthenticated_returns_401(self, client: TestClient):
        assert client.post("/events", json=CREATE_PAYLOAD).status_code == 401

    def test_member_returns_403(self, client: TestClient):
        with patch("app.dependencies.auth.get_profile",
                   return_value=mock_profile(USER_ID_MEMBER, "member")):
            r = client.post("/events", json=CREATE_PAYLOAD,
                            headers=auth_header("member", USER_ID_MEMBER))
        assert r.status_code == 403

    def test_staff_can_create(self, client: TestClient):
        with patch("app.dependencies.auth.get_profile",
                   return_value=mock_profile(USER_ID_STAFF, "staff")), \
             patch("app.crud.events.create_event", return_value=MOCK_EVENT):
            r = client.post("/events", json=CREATE_PAYLOAD,
                            headers=auth_header("staff", USER_ID_STAFF))
        assert r.status_code == 201
        assert r.json()["title"] == "Sunday Service"

    def test_admin_can_create(self, client: TestClient):
        with patch("app.dependencies.auth.get_profile",
                   return_value=mock_profile(USER_ID_ADMIN, "admin")), \
             patch("app.crud.events.create_event", return_value=MOCK_EVENT):
            r = client.post("/events", json=CREATE_PAYLOAD,
                            headers=auth_header("admin", USER_ID_ADMIN))
        assert r.status_code == 201

    def test_missing_title_returns_422(self, client: TestClient):
        with patch("app.dependencies.auth.get_profile",
                   return_value=mock_profile(USER_ID_STAFF, "staff")):
            r = client.post(
                "/events",
                json={"start_at": "2026-06-01T10:00:00Z", "end_at": "2026-06-01T11:00:00Z"},
                headers=auth_header("staff", USER_ID_STAFF),
            )
        assert r.status_code == 422

    def test_missing_start_at_returns_422(self, client: TestClient):
        with patch("app.dependencies.auth.get_profile",
                   return_value=mock_profile(USER_ID_STAFF, "staff")):
            r = client.post(
                "/events",
                json={"title": "Test", "end_at": "2026-06-01T11:00:00Z"},
                headers=auth_header("staff", USER_ID_STAFF),
            )
        assert r.status_code == 422


# ---------------------------------------------------------------------------
# PATCH /events/{id} — staff+
# ---------------------------------------------------------------------------
class TestUpdateEvent:
    def test_unauthenticated_returns_401(self, client: TestClient):
        assert client.patch(f"/events/{MOCK_EVENT['id']}",
                            json=UPDATE_PAYLOAD).status_code == 401

    def test_member_returns_403(self, client: TestClient):
        with patch("app.dependencies.auth.get_profile",
                   return_value=mock_profile(USER_ID_MEMBER, "member")):
            r = client.patch(f"/events/{MOCK_EVENT['id']}", json=UPDATE_PAYLOAD,
                             headers=auth_header("member", USER_ID_MEMBER))
        assert r.status_code == 403

    def test_staff_can_update(self, client: TestClient):
        updated = {**MOCK_EVENT, "description": "Updated description.", "is_published": True}
        with patch("app.dependencies.auth.get_profile",
                   return_value=mock_profile(USER_ID_STAFF, "staff")), \
             patch("app.crud.events.get_event", return_value=MOCK_EVENT), \
             patch("app.crud.events.update_event", return_value=updated):
            r = client.patch(f"/events/{MOCK_EVENT['id']}", json=UPDATE_PAYLOAD,
                             headers=auth_header("staff", USER_ID_STAFF))
        assert r.status_code == 200
        assert r.json()["description"] == "Updated description."

    def test_patch_nonexistent_returns_404(self, client: TestClient):
        with patch("app.dependencies.auth.get_profile",
                   return_value=mock_profile(USER_ID_STAFF, "staff")), \
             patch("app.crud.events.get_event", return_value=None):
            r = client.patch("/events/does-not-exist", json=UPDATE_PAYLOAD,
                             headers=auth_header("staff", USER_ID_STAFF))
        assert r.status_code == 404


# ---------------------------------------------------------------------------
# DELETE /events/{id} — admin+
# ---------------------------------------------------------------------------
class TestDeleteEvent:
    def test_unauthenticated_returns_401(self, client: TestClient):
        assert client.delete(f"/events/{MOCK_EVENT['id']}").status_code == 401

    def test_staff_cannot_delete(self, client: TestClient):
        with patch("app.dependencies.auth.get_profile",
                   return_value=mock_profile(USER_ID_STAFF, "staff")):
            r = client.delete(f"/events/{MOCK_EVENT['id']}",
                              headers=auth_header("staff", USER_ID_STAFF))
        assert r.status_code == 403

    def test_admin_can_delete(self, client: TestClient):
        with patch("app.dependencies.auth.get_profile",
                   return_value=mock_profile(USER_ID_ADMIN, "admin")), \
             patch("app.crud.events.get_event", return_value=MOCK_EVENT), \
             patch("app.crud.events.delete_event", return_value=None):
            r = client.delete(f"/events/{MOCK_EVENT['id']}",
                              headers=auth_header("admin", USER_ID_ADMIN))
        assert r.status_code == 204

    def test_delete_nonexistent_returns_404(self, client: TestClient):
        with patch("app.dependencies.auth.get_profile",
                   return_value=mock_profile(USER_ID_ADMIN, "admin")), \
             patch("app.crud.events.get_event", return_value=None):
            r = client.delete("/events/does-not-exist",
                              headers=auth_header("admin", USER_ID_ADMIN))
        assert r.status_code == 404
