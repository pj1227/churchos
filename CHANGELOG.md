# Changelog

All notable changes to ChurchOS are documented here.
Follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) format.

---

## [Unreleased]

### In progress
- Phase 6: Gloo AI integration

---

## [0.2.0] — 2026-05-29 "Kootenai" pre-release

### Phase 5 — Prayer Board

#### Added
- `public.prayer_requests` table — UUID PK, canonical schema (body, name, email, ai_score, ai_reason, moderated_at/by, is_answered, prayer_count, expires_at); RLS enabled
- `public.church_events` — migrated PK from VARCHAR to UUID
- API: `POST /prayer-requests` (public, rate-limited 3/hr/IP, Grok AI moderated)
- API: `GET /prayer-requests` (member+), `GET /prayer-requests/pending` (staff+), `PATCH /prayer-requests/{id}` (staff+)
- Rate limiting via Upstash Redis (`UPSTASH_REDIS_URL`, `UPSTASH_REDIS_TOKEN`); fail-open
- AI moderation via xAI Grok (`GROK_API_KEY`); fail-open; Phase 6 will add Gloo as primary
- `apps/web/app/pages/prayer.vue` — public prayer submission form; Prayer added to nav and footer
- `apps/admin/app/pages/prayer/index.vue` — staff moderation queue; Prayer added to admin sidebar
- 52 new tests (20 API + 10 web + 12 admin + layout updates); all passing

#### Architecture
- Documented ChurchOS as single-tenant portable CMS (Phase 9 = portability, not multi-tenancy)
- UUID PK convention established for all new tables going forward

---

## [0.1.0] — 2026-05-28 "Kootenai" pre-release

### Phase 4 — Admin Dashboard

#### Added
- `apps/admin` — Full admin dashboard Nuxt 4 application
- `layouts/default.vue` — Persistent sidebar with ChurchOS brand, nav, version badge; topbar with user identity and sign-out
- `pages/index.vue` — Dashboard landing page with quick-nav cards to Sermons and Events
- `pages/sermons/index.vue` — Sermon list table with Published/Draft badges and edit links
- `pages/sermons/[id]/edit.vue` — Sermon PATCH form; preserves Logos-synced fields
- `pages/events/index.vue` — Event list table with Published/Draft badges and edit links
- `pages/events/[id]/edit.vue` — Event PATCH form with all fields and toggles
- `apps/api/app/dependencies/rbac.py` — `require_role()` dependency factory (guest → superadmin)
- Sermon and Event schemas, models, CRUD, and routers
- Alembic migrations for `sermons` and `church_events` tables
- `CHURCH_ID` env var support; guard returns `[]` when not configured

#### Fixed
- Replaced `python-jose` with `PyJWT>=2.8.0` (incompatible with `cryptography>=42` on Railway Python 3.13)
- Removed unused `import pytest` flagged by ruff F401
- `pnpm-lock.yaml` stale `@railway/cli` specifier removed
- `IndexError` in `main.py` when resolving parent paths in Railway container

#### Infrastructure
- Railway env vars configured: `CHURCH_ID`, `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`, `SUPABASE_JWT_SECRET`
- API live: https://churchos-production-c6ae.up.railway.app
- `/sermons` returning live Logos-synced data in production
- `/events` returning `[]` (no events created yet — expected)

---

### Phase 3 — Supabase Auth & Database

#### Added
- Supabase Auth integration with JWT verification (PyJWT, HS256)
- `public.profiles` table with RBAC roles
- `public.churches` table (`id: "default"`, name: "Libby Church of the Nazarene")
- `public.sermons` table (Logos-synced, VARCHAR PKs, RLS enabled)
- `public.church_events` table
- `GET /me` endpoint — returns authenticated user's profile
- Row Level Security on `profiles` and `sermons`

---

### Phase 2 — Public Website

#### Added
- Public-facing Nuxt 4 site: homepage, sermons, about, contact
- Static generation via Cloudflare Pages (Nitro cloudflare-pages preset)
- Currently uses mock sermon/event data (live API wiring deferred to Phase 10)

---

### Phase 1 — Design System

#### Added
- Tailwind CSS v4 design tokens: forest, kootenai, gold, charcoal, stone palettes
- Font stack: Cinzel (display), Lora (body/scripture), DM Sans (UI)
- Shared component classes: btn-primary, btn-secondary, btn-ghost, co-card, etc.
- Dark mode via @nuxtjs/color-mode (class strategy)
- `packages/ui` shared component library

---

### Phase 0 — Repo & Tooling

#### Added
- pnpm workspaces + Turborepo monorepo scaffold
- GitHub Actions CI: turbo pipeline + pytest pipeline
- Cloudflare Pages deployment (production + staging)
- Railway.app deployment (FastAPI backend)
- Branch protection on main, staging, dev (PRs + CI required)
- `version.json` — semantic versioning visible in footer, admin topbar, `/health`
- `GET /health` → `{"status":"ok","version":"0.1.0","codename":"Kootenai"}`
