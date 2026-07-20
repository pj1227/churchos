# ChurchOS Developer Guide

**Version:** 0.1.0 pre-release ("Kootenai")
**Last updated:** Phase 7 — Gloo AI Integration
**Audience:** New contributors getting oriented in the codebase

---

## Table of Contents

- [1. What ChurchOS Is](#1-what-churchos-is)
- [2. Architecture Overview](#2-architecture-overview)
- [3. Local Development Setup](#3-local-development-setup)
- [4. How the Apps Talk to Each Other](#4-how-the-apps-talk-to-each-other)
- [5. Authentication & Authorization](#5-authentication--authorization)
- [6. The Connector Framework](#6-the-connector-framework)
- [7. Testing Conventions](#7-testing-conventions)
- [8. How to Add a Feature](#8-how-to-add-a-feature)
- [9. Git Workflow](#9-git-workflow)
- [10. Deployment](#10-deployment)
- [11. Database Conventions](#11-database-conventions)
- [12. Security Rules](#12-security-rules)

---

## 1. What ChurchOS Is

ChurchOS is a **single-tenant, portable CMS** — not a SaaS platform. Each church gets their own isolated deployment: their own Supabase project, their own Railway service, their own Cloudflare account. There is no shared database and no cross-church data isolation needed in code.

"Multi-church support" (Phase 9) means portability and easy self-hosting — not multi-tenancy. A church clones the repo, sets up their own accounts, and deploys.

The consequence: `church_id` on every table is always the string `"default"`. It stays in the schema for self-documentation but queries never filter across church IDs.

**Current state:** Phases 0–7 complete. The public site, admin dashboard, prayer board, connector framework, and Gloo AI integration are all live and tested.

---

## 2. Architecture Overview

```
                    ┌─────────────────────────────────────┐
                    │         Cloudflare Pages            │
                    │   apps/web   │   apps/admin         │
                    │  (Nuxt 4)    │   (Nuxt 4)           │
                    └──────┬───────┴──────┬───────────────┘
                           │              │
                  HTTPS + Bearer JWT      │
                           │              │
                    ┌──────▼──────────────▼───────────────┐
                    │       Railway.app — FastAPI          │
                    │          apps/api                    │
                    │                                      │
                    │  /health  /sermons  /events          │
                    │  /prayer-requests  /site-config      │
                    └──────┬────────────────┬─────────────┘
                           │                │
               Supabase REST/PostgREST   Upstash Redis
               (auth + database)         (rate limiting)
```

### Monorepo structure

```
churchos/
├── apps/
│   ├── web/              # Public-facing Nuxt 4 site
│   │   └── app/
│   │       ├── pages/    # index, sermons, about, contact, prayer/*, give
│   │       ├── layouts/  # default.vue (nav + footer)
│   │       └── components/  # AppNav, AppFooter
│   ├── admin/            # Staff admin dashboard (Nuxt 4)
│   │   └── app/
│   │       ├── pages/    # index, sermons/*, events/*, prayer/*, settings/*
│   │       ├── layouts/  # default.vue (sidebar + topbar)
│   │       ├── stores/   # auth.ts (Pinia)
│   │       └── middleware/  # auth.ts (route guard)
│   └── api/              # FastAPI backend
│       ├── app/
│       │   ├── main.py   # App entry point, router registration
│       │   ├── config.py # Settings (pydantic-settings)
│       │   ├── routers/  # me, sermons, events, prayer_requests, site_config
│       │   ├── schemas/  # Pydantic request/response models
│       │   ├── crud/     # Supabase REST calls
│       │   ├── models/   # SQLAlchemy models (for Alembic migrations)
│       │   ├── dependencies/  # auth, rbac, rate_limit, ai_moderation
│       │   ├── connectors/    # provider framework (email, AI)
│       │   └── services/      # email.py (thin wrapper)
│       ├── tests/        # pytest test suite
│       └── alembic/      # database migrations
├── packages/
│   ├── ui/               # Shared Vue component library (@churchos/ui)
│   ├── config/           # Shared Tailwind design tokens
│   ├── types/            # Shared TypeScript types
│   ├── maps/             # Pluggable map component
│   └── office-info/      # Service times, contact info (static data)
├── version.json          # { "version": "0.1.0", "codename": "Kootenai" }
├── turbo.json            # Turborepo pipeline config
├── pnpm-workspace.yaml   # Workspace package declarations
├── CLAUDE.md             # AI-assistant context file
├── PLAN.md               # Phase-by-phase build plan
└── CHANGELOG.md          # Release history
```

---

## 3. Local Development Setup

### Prerequisites

- Node.js 20+
- pnpm 9+ (`npm install -g pnpm`)
- Python 3.12+
- Git

### Step 1 — Clone and install

```bash
git clone https://github.com/pj1227/churchos.git
cd churchos
pnpm install          # installs all workspace packages
```

### Step 2 — Set up the API environment

```bash
cd apps/api
cp .env.example .env
```

Edit `.env` and fill in your values:

```bash
# Required for local dev (get from your Supabase project → Settings → API)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-secret-key
SUPABASE_JWT_SECRET=your-jwt-secret

# Optional — leave blank to skip rate limiting locally
UPSTASH_REDIS_URL=
UPSTASH_REDIS_TOKEN=

# Optional — leave blank to skip AI moderation locally (requests approved by default)
GROK_API_KEY=

# Email — leave blank to skip notifications locally
SMTP_HOST=
SMTP_USER=
SMTP_PASSWORD=
```

Install Python dependencies:

```bash
cd apps/api
pip install -r requirements.txt
```

### Step 3 — Set up the frontend environments

```bash
cd apps/web
cp .env.example .env.local
# Set NUXT_PUBLIC_API_BASE=http://localhost:8000
# Set NUXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
# Set NUXT_PUBLIC_SUPABASE_ANON_KEY=your-publishable-key

cd apps/admin
cp .env.example .env.local
# Same variables as apps/web
```

### Step 4 — Start the development servers

You need three terminals:

```bash
# Terminal 1 — API server
cd apps/api
uvicorn app.main:app --reload --port 8000

# Terminal 2 — Public website
cd apps/web
pnpm dev          # runs on http://localhost:3000

# Terminal 3 — Admin dashboard
cd apps/admin
pnpm dev          # runs on http://localhost:3001
```

Or run all from the repo root using Turborepo:

```bash
turbo dev
```

### Step 5 — Verify your setup

- Public site: [http://localhost:3000](http://localhost:3000)
- Admin dashboard: [http://localhost:3001](http://localhost:3001)
- API health: [http://localhost:8000/health](http://localhost:8000/health)

The health endpoint should return:
```json
{ "status": "ok", "version": "0.1.0", "codename": "Kootenai" }
```

---

## 4. How the Apps Talk to Each Other

### Frontend → API

Both Nuxt apps communicate with the FastAPI backend over HTTPS. In the admin app, the auth store reads the Supabase session and attaches the JWT as a Bearer token:

```typescript
// apps/admin/app/stores/auth.ts
const data = await $fetch<Profile>('/api/me', {
  headers: { Authorization: `Bearer ${session.access_token}` },
})
```

The public web app uses `useRuntimeConfig().public.apiBase` for the API base URL, configured via `NUXT_PUBLIC_API_BASE` in the environment.

### The /me endpoint — why it exists

Supabase Auth gives you the user's identity (email, UUID). But it doesn't know about ChurchOS-specific fields like `role` and `church_slug`. The `/me` endpoint bridges the gap:

1. Frontend sends a valid Supabase JWT to `GET /me`
2. API verifies the JWT and extracts the `sub` (user UUID) claim
3. API looks up `public.profiles` using the service role key (bypasses RLS)
4. Returns the profile row, including `role` and `church_slug`

The frontend stores this profile in Pinia memory — never in localStorage.

### Version as single source of truth

`version.json` at the repo root is the only place the version is defined:

```json
{ "version": "0.1.0", "codename": "Kootenai" }
```

`apps/api/app/main.py` reads this file at startup and returns it from `GET /health`. The admin layout reads `VERSION` and `CODENAME` from a hardcoded const today — this should eventually be wired to the health endpoint.

---

## 5. Authentication & Authorization

### The JWT flow

```
Browser                    FastAPI                    Supabase
   │                          │                          │
   │  POST /auth/signin        │                          │
   │─────────────────────────>│                          │
   │  (via Supabase JS SDK)    │  (Supabase handles)      │
   │<─────────────────────────│                          │
   │  access_token (JWT)       │                          │
   │  refresh_token (HttpOnly) │                          │
   │                          │                          │
   │  GET /me                  │                          │
   │  Authorization: Bearer JWT│                          │
   │─────────────────────────>│                          │
   │                          │  verify JWT (HS256)       │
   │                          │  lookup public.profiles   │
   │                          │  (service role key)       │
   │<─────────────────────────│                          │
   │  { role, church_slug, … } │                          │
```

**Token storage rules (non-negotiable):**
- Access tokens live in Pinia reactive memory only — never `localStorage`
- Refresh tokens are in an HttpOnly cookie managed by Supabase SSR
- The service role key is server-side only — never sent to the browser

### JWT verification (API)

`apps/api/app/dependencies/auth.py` handles verification using PyJWT:

```python
import jwt
from jwt.exceptions import InvalidTokenError

payload = jwt.decode(
    credentials.credentials,
    settings.supabase_jwt_secret,
    algorithms=["HS256"],
    options={"verify_aud": False},  # Supabase omits aud on JS client tokens
)
```

**Important:** This project uses `PyJWT` (import as `import jwt`), not `python-jose`. Catch `jwt.exceptions.InvalidTokenError`, not `JWTError`.

### RBAC — role enforcement

`apps/api/app/dependencies/rbac.py` provides `require_role()`, a dependency factory:

```python
_ROLE_RANK = {
    "guest":      0,
    "member":     1,
    "staff":      2,
    "admin":      3,
    "superadmin": 4,
}

def require_role(minimum: str):
    async def _check(current_user: dict = Depends(get_current_user)) -> dict:
        user_rank = _ROLE_RANK.get(current_user.get("role", "guest"), 0)
        if user_rank < _ROLE_RANK[minimum]:
            raise HTTPException(status_code=403, detail=f"Requires '{minimum}' role.")
        return current_user
    return _check
```

Usage in a router:

```python
@router.get("/prayer-requests/pending")
async def list_pending(current_user=Depends(require_role("staff"))):
    ...

@router.delete("/sermons/{id}")
async def delete_sermon(current_user=Depends(require_role("admin"))):
    ...
```

### Auth middleware (frontend)

`apps/admin/app/middleware/auth.ts` runs on every route transition and redirects to `/login` if `isAuthenticated` is false. Protected pages add:

```vue
<script setup lang="ts">
definePageMeta({ middleware: 'auth' })
</script>
```

---

## 6. The Connector Framework

The connector framework (Phase 6) is a plugin-style provider system. Each category (email, AI moderation) defines a Python ABC. The active provider is read from `site_config` at call time. Swapping providers requires only a database config change — no code changes.

### Email connectors

```
connectors/
  base/
    email.py          # EmailConnector ABC
  providers/
    email/
      smtp.py         # SmtpEmailConnector
      ms365.py        # Ms365EmailConnector (Graph API)
  registry.py         # get_email_connector() factory
```

The ABC defines the interface:

```python
# connectors/base/email.py
class EmailConnector(ABC):

    @abstractmethod
    def send_email(self, to, subject, body_text, body_html=None) -> bool:
        """Returns True on success, False on failure. Never raises."""

    @abstractmethod
    def send_prayer_notification(self, to, prayer_body, submitter_name, is_anonymous) -> bool:
        """Sends a prayer chain notification. Returns True/False."""
```

The registry reads `site_config` and returns the right provider:

```python
# connectors/registry.py
def get_email_connector() -> EmailConnector:
    provider = get_raw_value("email_provider") or "smtp"

    if provider == "ms365":
        # load credentials, return Ms365EmailConnector
        # falls back to SMTP if credentials incomplete
        ...

    return SmtpEmailConnector()  # default
```

**Fallback policy:** Unknown providers and incomplete credentials both fall back to SMTP, silently. A misconfigured `site_config` never breaks email delivery.

### AI connectors (Phase 7)

Same pattern as email. `get_ai_connector()` returns either `GrokAiConnector` (default) or `GlooAiConnector` based on `ai_provider` in `site_config`.

```
connectors/
  base/
    ai.py             # AiConnector ABC with moderate() method
  providers/
    ai/
      grok.py         # GrokAiConnector — grok-3-mini, OpenAI-compatible endpoint
      gloo.py         # GlooAiConnector — faith-context, OAuth2 client credentials
  registry.py         # get_ai_connector() factory
```

**Grok** (`providers/ai/grok.py`) — calls `https://api.x.ai/v1/chat/completions` with `grok-3-mini`. Uses a system prompt tuned for church prayer board moderation. The `GROK_API_KEY` env var is the only required config. Fail-open if no key or any exception.

**Gloo** (`providers/ai/gloo.py`) — faith-context AI designed for churches. Uses OAuth2 client credentials (`gloo_client_id` + `gloo_client_secret` from `site_config`) to obtain an access token from `https://api.gloo.chat/oauth/token`. Sends the prayer text with a `tradition` field (e.g., `"nazarene"`) to `https://api.gloo.chat/v1/moderate`. Fail-open on any exception.

**Fallback chain:** Gloo (if `ai_provider=gloo` and credentials present) → Grok → fail-open (approve submission). The system never silently drops a prayer request due to an AI failure.

**Patching in tests:**

```python
# The dependency is ai_moderation.moderate_prayer_request, not the connector directly
with patch("app.dependencies.ai_moderation.moderate_prayer_request", return_value=True):
    response = client.post("/prayer-requests", json={"body": "Please pray for..."})
assert response.status_code == 201
```

**Admin note:** The admin app (`apps/admin`) is configured as `ssr: false` (client-only SPA). This requires `@pinia/nuxt 0.11.3` for Nuxt 4 compatibility — do not upgrade this dependency without verifying Nuxt 4 SSR-off support.

### Adding a new connector provider

1. Create `connectors/providers/<category>/<provider_name>.py` implementing the ABC.
2. Add a branch to `registry.py` to recognize the new provider string.
3. Add a corresponding section to the Settings UI in `apps/admin/app/pages/settings/index.vue`.
4. Add `site_config` keys for any credentials to `apps/api/app/crud/site_config.py`.
5. Write tests in `apps/api/tests/test_connectors.py`.

---

## 7. Testing Conventions

### TDD rule — no exceptions

Write a failing test before writing implementation code. Every time. A phase is not done until all tests pass.

### API tests (pytest)

Run from `apps/api`:

```bash
cd apps/api
python -m pytest --tb=short
```

The test suite uses a hermetic setup — no real Supabase project is contacted:

```python
# tests/conftest.py
TEST_JWT_SECRET = "test-jwt-secret-for-pytest-only-32chars!!"
settings.supabase_jwt_secret = TEST_JWT_SECRET
settings.supabase_url = "https://test.supabase.co"
settings.supabase_service_key = "test-service-role-key"

@pytest.fixture
def client() -> TestClient:
    return TestClient(app)
```

**Generating test JWTs:**

```python
import jwt, time, uuid

def make_token(role: str, user_id: str = None) -> str:
    payload = {
        "sub": user_id or str(uuid.uuid4()),
        "role": role,
        "exp": int(time.time()) + 3600,
    }
    return jwt.encode(payload, TEST_JWT_SECRET, algorithm="HS256")
```

**Patching dependencies:** Functions that call Supabase or Redis are patched in tests using `unittest.mock.patch`. The internal `_redis_incr` function in `rate_limit.py` is intentionally extracted to make it patchable without a real Redis connection:

```python
from unittest.mock import patch

def test_rate_limit_exceeded(client):
    with patch("app.dependencies.rate_limit._redis_incr", return_value=4):
        response = client.post("/prayer-requests", json={"body": "Test"})
    assert response.status_code == 429
```

Similarly, `get_profile` in `auth.py` is a plain function (not a Depends) specifically so it can be patched cleanly:

```python
with patch("app.dependencies.auth.get_profile", return_value={"role": "staff", ...}):
    response = client.get("/prayer-requests/pending", headers={"Authorization": f"Bearer {token}"})
```

### Frontend tests (Vitest)

Run from each app:

```bash
cd apps/admin
pnpm test

cd apps/web
pnpm test
```

**Important Vitest gotcha for admin tests:** `useRoute` must be stubbed as a global in `tests/setup.ts`. Components must NOT import from `#app` — use Nuxt auto-imports (no explicit import statement). Test files override route params with:

```typescript
vi.stubGlobal('useRoute', () => ({ params: { id: 'some-id' } }))
```

**Important package gotcha:** Any Nuxt app running Vitest must declare `vue` in its own `devDependencies`. Even though Nuxt provides Vue, Vitest's transform pipeline requires a local resolution. If you add a new app, add `"vue": "..."` to its `package.json` devDependencies or tests will fail with a resolution error.

### Current test coverage

**API (`apps/api`):**

| File | Tests | What it covers |
|---|---|---|
| `test_health.py` | 1 | GET /health → 200 + version |
| `test_auth.py` | 8 | JWT verify, RBAC, profile lookup |
| `test_sermons.py` | 37 | Sermon CRUD endpoints |
| `test_events.py` | ~10 | Event CRUD endpoints |
| `test_prayer_requests.py` | 24 | Prayer board (submit, list, moderate) |
| `test_site_config.py` | ~8 | Site config CRUD |
| `test_connectors.py` | 14 | Email connector ABC, SMTP, MS365, registry |
| `test_ai_connectors.py` | ~8 | Grok + Gloo connectors, fallback chain |

**Admin (`apps/admin`):**

| File | Tests | What it covers |
|---|---|---|
| `tests/placeholder.test.ts` | 1 | Vitest smoke test |
| `tests/stores/auth.test.ts` | 8 | Pinia auth store |
| `tests/layouts/AdminLayout.test.ts` | 8 | Sidebar, topbar, slot, sign-out |
| `tests/pages/DashboardPage.test.ts` | 3 | Welcome page |
| `tests/pages/SermonsIndexPage.test.ts` | 7 | Sermon list |
| `tests/pages/SermonEditPage.test.ts` | 10 | Edit form, PATCH |
| `tests/pages/EventsIndexPage.test.ts` | 7 | Event list |
| `tests/pages/EventEditPage.test.ts` | 8 | Edit form, PATCH |
| `tests/pages/PrayerQueuePage.test.ts` | 16 | Moderation queue, approve/reject |
| `tests/pages/SettingsPage.test.ts` | 15 | Prayer chain email, connector UI |

---

## 8. How to Add a Feature

This is the end-to-end pattern for adding a feature — from database to UI — following the TDD and incremental-build rules.

### Example: Adding a new API endpoint

Suppose you're adding `GET /announcements` to list church announcements.

**Step 1 — Write the failing test first**

```python
# apps/api/tests/test_announcements.py
from unittest.mock import patch

def test_list_announcements_returns_200(client):
    with patch("app.crud.announcements.list_announcements", return_value=[]):
        response = client.get("/announcements")
    assert response.status_code == 200
    assert response.json() == []
```

Run it. It fails. Good.

**Step 2 — Add the Pydantic schema**

```python
# apps/api/app/schemas/announcement.py
from pydantic import BaseModel

class AnnouncementRead(BaseModel):
    id: str
    title: str
    body: str
    church_id: str
    created_at: str
```

**Step 3 — Add the CRUD function**

```python
# apps/api/app/crud/announcements.py
import httpx
from app.config import settings

def list_announcements() -> list[dict]:
    url = f"{settings.supabase_url}/rest/v1/announcements"
    headers = {
        "apikey": settings.supabase_service_key,
        "Authorization": f"Bearer {settings.supabase_service_key}",
    }
    resp = httpx.get(url, headers=headers, params={"order": "created_at.desc"})
    resp.raise_for_status()
    return resp.json()
```

**Step 4 — Add the router**

```python
# apps/api/app/routers/announcements.py
from fastapi import APIRouter
from app.crud import announcements as crud
from app.schemas.announcement import AnnouncementRead

router = APIRouter(prefix="/announcements", tags=["announcements"])

@router.get("", response_model=list[AnnouncementRead])
async def list_announcements():
    return crud.list_announcements()
```

**Step 5 — Register the router in main.py**

```python
# apps/api/app/main.py
from app.routers import announcements as announcements_router
app.include_router(announcements_router.router)
```

**Step 6 — Run the test. It should pass now.**

```bash
cd apps/api
python -m pytest tests/test_announcements.py -v
```

**Step 7 — Add a migration (if the table doesn't exist yet)**

```bash
cd apps/api
alembic revision --autogenerate -m "create_announcements_table"
alembic upgrade head
```

**Step 8 — Commit**

```bash
git add .
git commit -m "feat: add GET /announcements endpoint (TDD, all tests passing)"
git push
```

### Adding a role-protected endpoint

For any endpoint that requires authentication, inject `require_role()`:

```python
# staff or above can see draft announcements
@router.get("/announcements/drafts")
async def list_drafts(current_user=Depends(require_role("staff"))):
    return crud.list_draft_announcements()
```

For public endpoints that don't require auth, use no dependency. For member-only endpoints:

```python
@router.get("/announcements/private")
async def list_private(current_user=Depends(require_role("member"))):
    ...
```

### Adding a new connector provider

See [Section 6 — The Connector Framework](#6-the-connector-framework).

---

## 9. Git Workflow

```
feature/* ──► dev ──► staging ──► main
```

- **Always** cut feature branches from `dev`, not from `main` or `staging`.
- `main`, `staging`, and `dev` are protected — PRs only, CI must pass.
- Never commit directly to `staging` or `main`.

### Branch naming

```
feature/phase-N-short-description
fix/short-description
```

### Commit message style

```
feat: add GET /announcements endpoint
fix: correct rate limit key prefix for prayer requests
chore: update requirements.txt (PyJWT 2.9.0)
test: add missing edge case for rejected prayer moderation
docs: update DEVELOPER-GUIDE through Phase 6
```

### Typical feature workflow

```bash
git checkout dev
git pull origin dev
git checkout -b feature/phase-7-gloo-ai

# ... write test, implement, confirm test passes ...

git add .
git commit -m "feat: add Gloo AI connector with Grok fallback"
git push -u origin feature/phase-7-gloo-ai

# Open PR → dev on GitHub
```

### PR template

When opening a PR, use this format for the title and description:

**Title:** `[Phase N] Short description of what this adds or fixes`

**Description:**

```markdown
## What this does
Brief description of the change.

## How to test
1. Step one
2. Step two

## Checklist
- [ ] Tests written first (TDD)
- [ ] All tests pass (`turbo test`)
- [ ] No regressions in adjacent tests
- [ ] CHANGELOG.md updated
```

---

## 10. Deployment

### Environments

| Branch | Environment | Services |
|---|---|---|
| `main` | Production | Cloudflare Pages (prod) + Railway (prod API) |
| `staging` | Staging | Cloudflare Pages (staging) + Railway (staging API) |
| `dev` | CI only | Runs tests on PR; no deployed environment |

### Railway (API)

The API deploys to Railway automatically on push to `main` (via `.github/workflows/deploy-production.yml`).

**Required Railway environment variables:**

| Variable | Value |
|---|---|
| `CHURCH_ID` | `default` |
| `SUPABASE_URL` | Your Supabase project URL |
| `SUPABASE_SERVICE_KEY` | Supabase secret key |
| `SUPABASE_JWT_SECRET` | Supabase JWT secret |
| `UPSTASH_REDIS_URL` | Your Upstash Redis URL |
| `UPSTASH_REDIS_TOKEN` | Your Upstash token |
| `GROK_API_KEY` | xAI Grok key (for AI moderation) |
| `SMTP_HOST` | SMTP server hostname |
| `SMTP_USER` | Sender email address |
| `SMTP_PASSWORD` | SMTP password |

The production API is at: `https://churchos-production-c6ae.up.railway.app`

### Cloudflare Pages (frontend)

Both `apps/web` and `apps/admin` deploy to the `churchos` project on Cloudflare Pages.

**Build settings for each app:**
- Build command: `pnpm build`
- Output directory: `.output/public`
- Root directory: `apps/web` (or `apps/admin`)

**Environment variables required:**

```bash
NUXT_PUBLIC_API_BASE=https://your-api.up.railway.app
NUXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NUXT_PUBLIC_SUPABASE_ANON_KEY=your-publishable-key
```

### Running the full test suite before deploying

```bash
# From repo root
turbo test

# Or individually:
cd apps/api && python -m pytest --tb=short
cd apps/admin && pnpm test
cd apps/web && pnpm test
```

---

## 11. Database Conventions

### Primary key conventions

These are intentional and important — do not change them without understanding the reason:

| Table | PK type | Why |
|---|---|---|
| `churches` | VARCHAR — value `"default"` | Singleton config row; string ID is self-documenting |
| `sermons` | VARCHAR(36) | Logos sync assigns these IDs externally; do not change PK type |
| `church_events` | UUID with `DEFAULT gen_random_uuid()` | Being migrated; all new tables follow this pattern |
| `prayer_requests` | UUID with `DEFAULT gen_random_uuid()` | Standard for all Phase 5+ tables |
| `profiles` | UUID | Matches `auth.users.id` (Supabase Auth) |

**Rule for new tables:** Use `UUID` with `DEFAULT gen_random_uuid()` as the primary key.

### Alembic migrations

Generate a new migration after changing a model:

```bash
cd apps/api
alembic revision --autogenerate -m "describe_the_change"
alembic upgrade head
```

**Known issue:** The existing Supabase schema was partially created manually before Alembic was introduced. Before running migrations, stamp the current state:

```bash
alembic stamp b2c3d4e5f6a7
```

### RLS policy status

RLS is active on all sensitive tables as of Phase 6. Migration `h8i9j0k1l2m3` added policies covering `site_config` (admin-only), `announcements` and `pages` (public read published / staff write), and `sermon_sync_logs` (staff read only). `alembic_version` is a system table not accessible via PostgREST — no RLS needed.

A full security audit of all policies is planned for Phase 12.

---

## 12. Security Rules

These rules are non-negotiable. Every PR must respect them.

| Rule | How it's enforced |
|---|---|
| Access tokens in memory only — never `localStorage` | `stores/auth.ts` — `profile` is a reactive ref, never persisted |
| Refresh tokens in HttpOnly cookies only | Supabase SSR handles this; we never touch refresh tokens directly |
| JWT verified server-side on every protected endpoint | `dependencies/auth.py` — `verify_token()` called before `get_current_user` |
| RLS active on all sensitive Supabase tables | Schema migrations; verified in Phase 12 audit |
| PII encrypted at rest (AES-256, column-level) | Required for member directory (Phase 9) — not yet implemented |
| Rate limiting via Redis on all write endpoints | `dependencies/rate_limit.py` — inject `Depends(check_rate_limit)` |
| Prayer submissions AI-moderated before going public | `dependencies/ai_moderation.py` — always runs on POST /prayer-requests |
| Directory requires member role minimum — never public | Enforced via `require_role("member")` on directory endpoints (Phase 9) |
| No bulk export endpoint for directory or giving records | Do not add `GET /members` or `GET /giving/all` without pagination + role gating |
| Stripe.js handles all card input — card data never touches our API | Enforced by Stripe integration design (Phase 8) |

### Fail-open vs. fail-closed

ChurchOS chooses **fail-open** for rate limiting and AI moderation. If Redis is unavailable, the rate limit check is skipped and the request proceeds. If AI moderation fails, the submission is stored as approved. This is intentional — a Redis outage or AI provider error should not silently drop a prayer request from a congregation member.

The exception: authentication always **fail-closed**. An invalid or missing JWT always returns 401.

---

*ChurchOS Developer Guide — updated with each phase release.*
*Current version: 0.1.0 pre-release | Phase 7 — Gloo AI Integration | Codename: "Kootenai"*
