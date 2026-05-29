"""
test_prayer_requests.py — TDD tests for the prayer board API.

Written before any implementation exists — all tests should FAIL on first run.

Endpoints under test:
  POST   /prayer-requests            guest (no auth)   — submit a prayer request
  GET    /prayer-requests            member+           — list approved requests
  GET    /prayer-requests/pending    staff+            — moderation queue
  PATCH  /prayer-requests/{id}       staff+            — approve or reject

Security contracts:
  - POST is unauthenticated but rate-limited (3/hr per IP via Redis)
  - POST goes through AI moderation before being stored/approved
  - GET /prayer-requests requires member role minimum
  - GET /prayer-requests/pending requires staff role minimum
  - PATCH requires staff role minimum
  - Rejected / pending requests are never returned in the public list

AI moderation contract (mocked in tests):
  - app.dependencies.ai_moderation.moderate_prayer_request(body: str) -> dict
  - Returns {"approved": True, "reason": None}   or   {"approved": False, "reason": "..."}
  - Approved  → status stored as "approved"
  - Rejected  → status stored as "rejected" (request still stored, 201 returned)
  - AI unavailable → fall through as "approved" (graceful degradation)

Rate limit contract (mocked in tests):
  - app.dependencies.rate_limit._redis_incr(key, ttl) -> int
  - Returns the new count after increment
  - count > RATE_LIMIT_MAX → 429 Too Many Requests
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
TEST_CHURCH_ID  = "default"
USER_ID_STAFF   = str(uuid.uuid4())
USER_ID_ADMIN   = str(uuid.uuid4())
USER_ID_MEMBER  = str(uuid.uuid4())
PRAYER_ID       = str(uuid.uuid4())

MOCK_PRAYER_APPROVED = {
    "id":           PRAYER_ID,
    "church_id":    TEST_CHURCH_ID,
    "name":         "Jane Doe",
    "body":         "Please pray for healing.",
    "is_anonymous": False,
    "status":       "approved",
    "ai_score":     0.95,
    "ai_reason":    None,
    "submitted_at": "2026-05-28T10:00:00Z",
    "moderated_at": None,
    "moderated_by": None,
    "is_answered":  False,
    "created_at":   "2026-05-28T10:00:00Z",
    "updated_at":   "2026-05-28T10:00:00Z",
}

MOCK_PRAYER_PENDING = {**MOCK_PRAYER_APPROVED, "status": "pending"}
MOCK_PRAYER_REJECTED = {**MOCK_PRAYER_APPROVED, "status": "rejected", "ai_reason": "Inappropriate content"}

SUBMIT_PAYLOAD = {
    "name":         "Jane Doe",
    "body":         "Please pray for healing.",
    "is_anonymous": False,
}

MODERATE_APPROVE = {"status": "approved"}
MODERATE_REJECT  = {"status": "rejected", "reason": "Inappropriate content"}


# ---------------------------------------------------------------------------
# JWT / auth helpers (same pattern as test_events.py)
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
    return {
        "id":           user_id,
        "role":         role,
        "church_id":    TEST_CHURCH_ID,
        "church_slug":  "libby-naz",
        "email":        f"{role}@test.com",
        "display_name": None,
    }


# ---------------------------------------------------------------------------
# POST /prayer-requests — public, rate-limited, AI-moderated
# ---------------------------------------------------------------------------
class TestSubmitPrayerRequest:
    def test_submit_succeeds_without_auth(self, client: TestClient):
        """Anyone can submit — no auth required."""
        with patch("app.dependencies.rate_limit._redis_incr", return_value=1), \
             patch("app.dependencies.ai_moderation.moderate_prayer_request",
                   return_value={"approved": True, "reason": None}), \
             patch("app.crud.prayer_requests.create_prayer_request",
                   return_value=MOCK_PRAYER_APPROVED):
            r = client.post("/prayer-requests", json=SUBMIT_PAYLOAD)
        assert r.status_code == 201
        assert r.json()["id"] == PRAYER_ID

    def test_body_is_required(self, client: TestClient):
        """Missing `body` field → 422 Unprocessable Entity."""
        with patch("app.dependencies.rate_limit._redis_incr", return_value=1):
            r = client.post("/prayer-requests", json={"name": "Jane"})
        assert r.status_code == 422

    def test_empty_body_rejected(self, client: TestClient):
        """Empty string body → 422."""
        with patch("app.dependencies.rate_limit._redis_incr", return_value=1):
            r = client.post("/prayer-requests", json={"body": ""})
        assert r.status_code == 422

    def test_anonymous_submission_allowed(self, client: TestClient):
        """is_anonymous=True and no name → valid submission."""
        anon_prayer = {**MOCK_PRAYER_APPROVED, "name": None, "is_anonymous": True}
        with patch("app.dependencies.rate_limit._redis_incr", return_value=1), \
             patch("app.dependencies.ai_moderation.moderate_prayer_request",
                   return_value={"approved": True, "reason": None}), \
             patch("app.crud.prayer_requests.create_prayer_request",
                   return_value=anon_prayer):
            r = client.post(
                "/prayer-requests",
                json={"body": "Pray for me.", "is_anonymous": True},
            )
        assert r.status_code == 201

    def test_rate_limit_429_when_exceeded(self, client: TestClient):
        """4th request from same IP in the window → 429."""
        with patch("app.dependencies.rate_limit._redis_incr", return_value=4):
            r = client.post("/prayer-requests", json=SUBMIT_PAYLOAD)
        assert r.status_code == 429
        assert "rate limit" in r.json()["detail"].lower()

    def test_ai_rejected_still_returns_201(self, client: TestClient):
        """
        If AI flags the content, the request is stored with status='rejected'
        but we still return 201 — submitter doesn't know it was rejected
        (dignity & privacy for the submitter).
        """
        with patch("app.dependencies.rate_limit._redis_incr", return_value=1), \
             patch("app.dependencies.ai_moderation.moderate_prayer_request",
                   return_value={"approved": False, "reason": "Inappropriate"}), \
             patch("app.crud.prayer_requests.create_prayer_request",
                   return_value=MOCK_PRAYER_REJECTED):
            r = client.post("/prayer-requests", json=SUBMIT_PAYLOAD)
        assert r.status_code == 201

    def test_ai_approved_has_approved_status(self, client: TestClient):
        """AI-approved submission → status='approved' in response."""
        with patch("app.dependencies.rate_limit._redis_incr", return_value=1), \
             patch("app.dependencies.ai_moderation.moderate_prayer_request",
                   return_value={"approved": True, "reason": None}), \
             patch("app.crud.prayer_requests.create_prayer_request",
                   return_value=MOCK_PRAYER_APPROVED):
            r = client.post("/prayer-requests", json=SUBMIT_PAYLOAD)
        assert r.json()["status"] == "approved"


# ---------------------------------------------------------------------------
# GET /prayer-requests — member+ required, returns only approved
# ---------------------------------------------------------------------------
class TestListApprovedPrayerRequests:
    def test_unauthenticated_returns_401(self, client: TestClient):
        r = client.get("/prayer-requests")
        assert r.status_code == 401

    def test_member_can_view_approved(self, client: TestClient):
        with patch("app.dependencies.auth.get_profile",
                   return_value=mock_profile(USER_ID_MEMBER, "member")), \
             patch("app.crud.prayer_requests.list_prayer_requests",
                   return_value=[MOCK_PRAYER_APPROVED]):
            r = client.get(
                "/prayer-requests",
                headers=auth_header("member", USER_ID_MEMBER),
            )
        assert r.status_code == 200
        assert r.json()[0]["status"] == "approved"

    def test_staff_can_view_approved(self, client: TestClient):
        with patch("app.dependencies.auth.get_profile",
                   return_value=mock_profile(USER_ID_STAFF, "staff")), \
             patch("app.crud.prayer_requests.list_prayer_requests",
                   return_value=[MOCK_PRAYER_APPROVED]):
            r = client.get(
                "/prayer-requests",
                headers=auth_header("staff", USER_ID_STAFF),
            )
        assert r.status_code == 200

    def test_returns_empty_list_when_none(self, client: TestClient):
        with patch("app.dependencies.auth.get_profile",
                   return_value=mock_profile(USER_ID_MEMBER, "member")), \
             patch("app.crud.prayer_requests.list_prayer_requests", return_value=[]):
            r = client.get(
                "/prayer-requests",
                headers=auth_header("member", USER_ID_MEMBER),
            )
        assert r.status_code == 200
        assert r.json() == []


# ---------------------------------------------------------------------------
# GET /prayer-requests/pending — staff+ moderation queue
# ---------------------------------------------------------------------------
class TestPendingQueue:
    def test_unauthenticated_returns_401(self, client: TestClient):
        r = client.get("/prayer-requests/pending")
        assert r.status_code == 401

    def test_member_returns_403(self, client: TestClient):
        with patch("app.dependencies.auth.get_profile",
                   return_value=mock_profile(USER_ID_MEMBER, "member")):
            r = client.get(
                "/prayer-requests/pending",
                headers=auth_header("member", USER_ID_MEMBER),
            )
        assert r.status_code == 403

    def test_staff_can_view_pending_queue(self, client: TestClient):
        with patch("app.dependencies.auth.get_profile",
                   return_value=mock_profile(USER_ID_STAFF, "staff")), \
             patch("app.crud.prayer_requests.list_prayer_requests",
                   return_value=[MOCK_PRAYER_PENDING]):
            r = client.get(
                "/prayer-requests/pending",
                headers=auth_header("staff", USER_ID_STAFF),
            )
        assert r.status_code == 200
        assert r.json()[0]["status"] == "pending"


# ---------------------------------------------------------------------------
# PATCH /prayer-requests/{id} — staff+ moderation action
# ---------------------------------------------------------------------------
class TestModeratePrayerRequest:
    def test_unauthenticated_returns_401(self, client: TestClient):
        r = client.patch(f"/prayer-requests/{PRAYER_ID}", json=MODERATE_APPROVE)
        assert r.status_code == 401

    def test_member_returns_403(self, client: TestClient):
        with patch("app.dependencies.auth.get_profile",
                   return_value=mock_profile(USER_ID_MEMBER, "member")):
            r = client.patch(
                f"/prayer-requests/{PRAYER_ID}",
                json=MODERATE_APPROVE,
                headers=auth_header("member", USER_ID_MEMBER),
            )
        assert r.status_code == 403

    def test_staff_can_approve(self, client: TestClient):
        approved = {**MOCK_PRAYER_APPROVED, "status": "approved", "moderated_by": USER_ID_STAFF}
        with patch("app.dependencies.auth.get_profile",
                   return_value=mock_profile(USER_ID_STAFF, "staff")), \
             patch("app.crud.prayer_requests.get_prayer_request",
                   return_value=MOCK_PRAYER_PENDING), \
             patch("app.crud.prayer_requests.moderate_prayer_request",
                   return_value=approved):
            r = client.patch(
                f"/prayer-requests/{PRAYER_ID}",
                json=MODERATE_APPROVE,
                headers=auth_header("staff", USER_ID_STAFF),
            )
        assert r.status_code == 200
        assert r.json()["status"] == "approved"

    def test_staff_can_reject(self, client: TestClient):
        rejected = {**MOCK_PRAYER_APPROVED, "status": "rejected", "moderated_by": USER_ID_STAFF}
        with patch("app.dependencies.auth.get_profile",
                   return_value=mock_profile(USER_ID_STAFF, "staff")), \
             patch("app.crud.prayer_requests.get_prayer_request",
                   return_value=MOCK_PRAYER_PENDING), \
             patch("app.crud.prayer_requests.moderate_prayer_request",
                   return_value=rejected):
            r = client.patch(
                f"/prayer-requests/{PRAYER_ID}",
                json=MODERATE_REJECT,
                headers=auth_header("staff", USER_ID_STAFF),
            )
        assert r.status_code == 200
        assert r.json()["status"] == "rejected"

    def test_nonexistent_returns_404(self, client: TestClient):
        with patch("app.dependencies.auth.get_profile",
                   return_value=mock_profile(USER_ID_STAFF, "staff")), \
             patch("app.crud.prayer_requests.get_prayer_request", return_value=None):
            r = client.patch(
                "/prayer-requests/does-not-exist",
                json=MODERATE_APPROVE,
                headers=auth_header("staff", USER_ID_STAFF),
            )
        assert r.status_code == 404

    def test_invalid_status_returns_422(self, client: TestClient):
        """Status must be 'approved' or 'rejected'."""
        with patch("app.dependencies.auth.get_profile",
                   return_value=mock_profile(USER_ID_STAFF, "staff")):
            r = client.patch(
                f"/prayer-requests/{PRAYER_ID}",
                json={"status": "banana"},
                headers=auth_header("staff", USER_ID_STAFF),
            )
        assert r.status_code == 422
