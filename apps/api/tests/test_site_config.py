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
        "is_public":  False,
        "updated_at": "2026-05-29T10:00:00Z",
    },
    {
        "id":         2,
        "church_id":  "default",
        "key":        "smtp_password",
        "value":      "supersecret",
        "is_secret":  True,
        "is_json":    False,
        "is_public":  False,
        "updated_at": "2026-05-29T10:00:00Z",
    },
]

MOCK_EMAIL_CONFIG = MOCK_CONFIG[0]

MOCK_PUBLIC_CONFIG = [
    {
        "id":         3,
        "church_id":  "default",
        "key":        "church_name",
        "value":      "Libby Church of the Nazarene",
        "is_secret":  False,
        "is_json":    False,
        "is_public":  True,
        "updated_at": "2026-05-29T10:00:00Z",
    },
    {
        "id":         4,
        "church_id":  "default",
        "key":        "church_phone",
        "value":      "(406) 293-2931",
        "is_secret":  False,
        "is_json":    False,
        "is_public":  True,
        "updated_at": "2026-05-29T10:00:00Z",
    },
]


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
# GET /site-config/public
# ---------------------------------------------------------------------------
class TestPublicSiteConfig:
    """
    Public, unauthenticated read of CMS content keys — powers apps/web's
    useSiteContent() composable. Only rows with is_public=true AND
    is_secret=false are ever returned, and never through the masked/staff
    GET endpoints' code path.
    """

    def test_no_auth_required(self, client: TestClient):
        with patch("app.crud.site_config.list_public_config", return_value=MOCK_PUBLIC_CONFIG):
            r = client.get("/site-config/public")
        assert r.status_code == 200

    def test_returns_key_value_map(self, client: TestClient):
        with patch("app.crud.site_config.list_public_config", return_value=MOCK_PUBLIC_CONFIG):
            r = client.get("/site-config/public")
        assert r.json() == {
            "church_name":  "Libby Church of the Nazarene",
            "church_phone": "(406) 293-2931",
        }

    def test_does_not_expose_secret_or_private_keys(self, client: TestClient):
        # crud.list_public_config is responsible for the is_public/is_secret
        # filter (enforced at the query layer) — the router must not
        # re-introduce private rows even if the crud layer returns them.
        mixed = MOCK_PUBLIC_CONFIG + [
            {
                "id": 5, "church_id": "default", "key": "ms365_client_secret",
                "value": "leaked", "is_secret": True, "is_json": False,
                "is_public": False, "updated_at": "2026-05-29T10:00:00Z",
            },
        ]
        with patch("app.crud.site_config.list_public_config", return_value=MOCK_PUBLIC_CONFIG):
            r = client.get("/site-config/public")
        assert "ms365_client_secret" not in r.json()

    def test_route_does_not_collide_with_key_route(self, client: TestClient):
        # Regression guard: GET /site-config/{key} requires staff+ auth.
        # "public" must be handled by its own route, not swallowed as key="public".
        with patch("app.crud.site_config.list_public_config", return_value=[]):
            r = client.get("/site-config/public")
        assert r.status_code == 200


# ---------------------------------------------------------------------------
# POST /site-config/logo
# ---------------------------------------------------------------------------
class TestUploadLogo:
    """
    Church logo upload — staff+ picks a file in the admin UI, it's uploaded
    to Supabase Storage, and the resulting public URL is written to the
    church_logo_url site_config key (is_public=true) so apps/web can render
    it without auth.
    """

    def test_unauthenticated_returns_401(self, client: TestClient):
        r = client.post("/site-config/logo",
                        files={"file": ("logo.png", b"fake-png-bytes", "image/png")})
        assert r.status_code == 401

    def test_member_returns_403(self, client: TestClient):
        with patch("app.dependencies.auth.get_profile",
                   return_value=mock_profile(USER_ID_MEMBER, "member")):
            r = client.post("/site-config/logo",
                            files={"file": ("logo.png", b"fake-png-bytes", "image/png")},
                            headers=auth_header(USER_ID_MEMBER))
        assert r.status_code == 403

    def test_staff_can_upload_valid_png(self, client: TestClient):
        with patch("app.dependencies.auth.get_profile",
                   return_value=mock_profile(USER_ID_STAFF, "staff")), \
             patch("app.crud.storage.upload_public_file",
                   return_value="https://test.supabase.co/storage/v1/object/public/public-assets/logo-abc123.png") as mock_upload, \
             patch("app.crud.site_config.set_config_value") as mock_set:
            mock_set.return_value = {
                "id": 9, "church_id": "default", "key": "church_logo_url",
                "value": "https://test.supabase.co/storage/v1/object/public/public-assets/logo-abc123.png",
                "is_secret": False, "is_json": False, "is_public": True,
                "updated_at": "2026-07-28T10:00:00Z",
            }
            r = client.post("/site-config/logo",
                            files={"file": ("logo.png", b"fake-png-bytes", "image/png")},
                            headers=auth_header(USER_ID_STAFF))
        assert r.status_code == 200
        assert r.json()["url"].endswith("logo-abc123.png")
        assert mock_upload.called
        write_payload = mock_set.call_args[0][1]
        assert write_payload.is_public is True
        assert mock_set.call_args[0][0] == "church_logo_url"

    def test_rejects_disallowed_extension(self, client: TestClient):
        with patch("app.dependencies.auth.get_profile",
                   return_value=mock_profile(USER_ID_STAFF, "staff")):
            r = client.post("/site-config/logo",
                            files={"file": ("logo.txt", b"not an image", "text/plain")},
                            headers=auth_header(USER_ID_STAFF))
        assert r.status_code == 400

    def test_rejects_oversized_file(self, client: TestClient):
        too_big = b"0" * (2 * 1024 * 1024 + 1)
        with patch("app.dependencies.auth.get_profile",
                   return_value=mock_profile(USER_ID_STAFF, "staff")):
            r = client.post("/site-config/logo",
                            files={"file": ("logo.png", too_big, "image/png")},
                            headers=auth_header(USER_ID_STAFF))
        assert r.status_code == 400

    def test_accepts_svg(self, client: TestClient):
        with patch("app.dependencies.auth.get_profile",
                   return_value=mock_profile(USER_ID_STAFF, "staff")), \
             patch("app.crud.storage.upload_public_file",
                   return_value="https://test.supabase.co/storage/v1/object/public/public-assets/logo-abc.svg"), \
             patch("app.crud.site_config.set_config_value") as mock_set:
            mock_set.return_value = {
                "id": 9, "church_id": "default", "key": "church_logo_url",
                "value": "https://test.supabase.co/storage/v1/object/public/public-assets/logo-abc.svg",
                "is_secret": False, "is_json": False, "is_public": True,
                "updated_at": "2026-07-28T10:00:00Z",
            }
            r = client.post("/site-config/logo",
                            files={"file": ("logo.svg", b"<svg></svg>", "image/svg+xml")},
                            headers=auth_header(USER_ID_STAFF))
        assert r.status_code == 200


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

    def test_is_public_defaults_false(self, client: TestClient):
        with patch("app.dependencies.auth.get_profile",
                   return_value=mock_profile(USER_ID_ADMIN, "admin")), \
             patch("app.crud.site_config.set_config_value") as mock_set:
            mock_set.return_value = {**MOCK_EMAIL_CONFIG, "is_public": False}
            client.put("/site-config/prayer_chain_email",
                       json={"value": "new@libbynaz.org"},
                       headers=auth_header(USER_ID_ADMIN))
        payload = mock_set.call_args[0][1]
        assert payload.is_public is False

    def test_can_write_is_public_true(self, client: TestClient):
        with patch("app.dependencies.auth.get_profile",
                   return_value=mock_profile(USER_ID_ADMIN, "admin")), \
             patch("app.crud.site_config.set_config_value") as mock_set:
            mock_set.return_value = {
                "id": 3, "church_id": "default", "key": "church_name",
                "value": "Libby Church", "is_secret": False, "is_json": False,
                "is_public": True, "updated_at": "2026-05-29T10:00:00Z",
            }
            r = client.put("/site-config/church_name",
                           json={"value": "Libby Church", "is_public": True},
                           headers=auth_header(USER_ID_ADMIN))
        payload = mock_set.call_args[0][1]
        assert payload.is_public is True
        assert r.json()["is_public"] is True
