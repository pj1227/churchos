# ChurchOS — CLAUDE.md

Project context and conventions for AI-assisted development.
This file is the source of truth for any new session.

---

## What this is

ChurchOS is a modular, open-source church CMS built for Libby Church of the Nazarene
and designed for multi-church deployment. It replaces the active church website.

**Version:** 0.1.0 pre-release — Release 1.0.0 is named "Kootenai"

---

## Stack

| Layer        | Technology                                      |
|--------------|-------------------------------------------------|
| Frontend     | Nuxt 4, Tailwind CSS v4                         |
| Backend      | FastAPI (Python 3.12), Supabase (PostgreSQL)    |
| Auth         | Supabase Auth, JWT (PyJWT), RBAC                |
| Monorepo     | pnpm workspaces + Turborepo                     |
| Frontend CD  | Cloudflare Pages                                |
| Backend CD   | Railway.app                                     |
| Cache        | Upstash Redis                                   |
| Storage      | Backblaze B2                                    |

---

## Monorepo structure

```
apps/
  web/      — Public-facing Nuxt 4 site (homepage, sermons, events, contact)
  admin/    — Admin dashboard Nuxt 4 app (CRUD, content management)
  api/      — FastAPI backend
packages/
  ui/       — Shared component library (design tokens, reusable Vue components)
  config/   — Shared TypeScript/ESLint/Tailwind configs
```

---

## Non-negotiable rules

- **TDD always.** Write a failing test before any implementation. No exceptions.
- **Explain every file.** What it does, why it exists, how it connects.
- **Incremental and verified.** One piece at a time, confirm it works, then move on.
- **Commit often.** git add → commit → push after each meaningful working unit.

---

## Git workflow

- `feature/*` branches cut from `dev`
- Merge path: `feature/*` → `dev` → `staging` → `main`
- `main`, `staging`, `dev` are protected — PRs only, CI must pass
- Never commit directly to `staging` or `main`
- Branch naming: `feature/phase-N-description` or `fix/short-description`

---

## RBAC roles

`superadmin → admin → staff → member → guest`

Enforced in `apps/api/app/dependencies/rbac.py` via `require_role()`.

---

## Security requirements (always enforce)

- Access tokens in memory only — never localStorage
- Refresh tokens in HttpOnly cookies only
- JWT verified server-side on every protected endpoint
- RLS active on all sensitive Supabase tables
- PII encrypted at rest (AES-256, column-level)
- Rate limiting via Redis on all write endpoints
- Prayer submissions AI-moderated before going public
- Directory requires member role minimum — never public
- No bulk export endpoint for directory or giving records
- Stripe.js handles all card input — card data never touches our API

---

## Design system

**Colors:** forest-500 (#2d6a4f) primary · kootenai-500 (#3a7d8c) secondary ·
gold-500 (#c9962b) accent · charcoal-900 (#0a1012) dark · stone-50 (#faf8f5) light

**Fonts:** Cinzel (display/h1-h2) · Lora (body/scripture) · DM Sans (UI/nav/buttons)

**Dark mode:** class strategy via @nuxtjs/color-mode

**Component classes:** `btn-primary`, `btn-secondary`, `btn-ghost`, `co-card`,
`co-card-featured`, `co-container`, `co-section`, `scripture-callout`,
`badge-forest`, `badge-kootenai`, `badge-gold`, `form-input`, `form-label`

---

## Deployed infrastructure

| Service         | URL / Location                                           |
|-----------------|----------------------------------------------------------|
| API (prod)      | https://churchos-production-c6ae.up.railway.app          |
| Public site     | Cloudflare Pages — `churchos` project                    |
| Admin           | Cloudflare Pages — `churchos` project                    |
| Supabase        | churchos-libbynaz project                                |

### Railway environment variables (all required)

| Variable              | Value / Source                               |
|-----------------------|----------------------------------------------|
| `CHURCH_ID`           | `default` (id of Libby Naz in public.churches) |
| `SUPABASE_URL`        | Supabase project URL                          |
| `SUPABASE_SERVICE_KEY`| Supabase **secret key** (formerly service role) |
| `SUPABASE_JWT_SECRET` | Supabase Settings → API → JWT Settings        |

> **Note:** Supabase renamed keys in 2025: "publishable" = anon key, "secret" = service role key.

---

## Deployment architecture (important)

ChurchOS is a **single-tenant, portable CMS**. Each church gets its own isolated
deployment — their own Supabase project, Railway service, and Cloudflare account.
There is no shared database and no cross-church data isolation needed in code.

Phase 9 ("Multi-church support") means **portability and easy self-hosting**, not
multi-tenancy. A church downloads the repo, sets up their own accounts, and deploys.

Consequence: `church_id` on every table is a per-deployment constant (always
`"default"`), not a tenant discriminator. It stays for self-documentation and
sanity-checking configuration, but queries are never filtering across church IDs.

---

## Supabase schema notes

### Primary key conventions
- `churches.id` — VARCHAR, value `"default"` — intentional singleton config row
- `sermons.id` — VARCHAR(36) — Logos-sync assigned; do not change PK type
- `church_events.id` — being migrated to UUID (table is empty, no external IDs)
- `prayer_requests.id` and all future tables — UUID with `DEFAULT gen_random_uuid()`

### Per-table notes
- `public.churches` — singleton row; `id = "default"` for Libby Naz
- `public.sermons` — Logos-synced; `church_id` FK; use PATCH not PUT
- `public.church_events` — manually managed; migrating PK to UUID
- `public.prayer_requests` — Phase 5; UUID PK; RLS enabled; full schema in migration d4e5f6a7b8c9
- `public.profiles` — RBAC roles stored here; linked to `auth.users` (UUID)
- **RLS:** All tables now have RLS enabled. Migration `h8i9j0k1l2m3` covers
  `site_config` (admin-only), `announcements` and `pages` (public read published /
  staff write), `sermon_sync_logs` (staff read only). `alembic_version` is a
  system table — not accessible via PostgREST, no RLS needed.

---

## Phase status

| Phase | Name                          | Status         |
|-------|-------------------------------|----------------|
| 0     | Repo & tooling                | ✅ Complete     |
| 1     | Design system                 | ✅ Complete     |
| 2     | Public website                | ✅ Complete (mock data — wired to API in Phase 12) |
| 3     | Supabase auth & database      | ✅ Complete     |
| 4     | Admin dashboard               | ✅ Complete     |
| 5     | Prayer board                  | ✅ Complete     |
| 5b    | Prayer board completion       | ✅ Complete     |
| 6     | Connector framework           | ✅ Complete     |
| 7     | Gloo AI integration           | ✅ Complete     |
| 8     | Giving module (Stripe)        | ⬜ Not started  |
| 9     | Member directory              | ⬜ Not started  |
| 10    | Auth providers (MS365/Google) | ⬜ Not started  |
| 11    | Advanced connectors           | ⬜ Not started  |
| 12    | Polish & hardening            | ⬜ Not started  |

---

## Connector framework (Phases 6–7)

Connector categories use Python ABCs so providers are swappable via `site_config`
with no code changes. The registry reads the provider key at call time.

```
apps/api/app/connectors/
  base/email.py              — EmailConnector ABC
  base/ai.py                 — AiConnector ABC
  providers/email/smtp.py    — SmtpEmailConnector (default, env-var driven)
  providers/email/ms365.py   — Ms365EmailConnector (Graph API, OAuth2)
  providers/ai/grok.py       — GrokAiConnector (grok-3-mini, OpenAI-compatible API)
  providers/ai/gloo.py       — GlooAiConnector (faith-context, OAuth2 client credentials)
  registry.py                — get_email_connector() + get_ai_connector() factories
```

**Active providers** are set in `site_config` table:

| Key                   | Values            | Default |
|-----------------------|-------------------|---------|
| `email_provider`      | `smtp` / `ms365`  | `smtp`  |
| `ms365_tenant_id`     | Azure tenant UUID | —       |
| `ms365_client_id`     | Azure app UUID    | —       |
| `ms365_client_secret` | Secret (masked)   | —       |
| `ms365_sender`        | Licensed mailbox  | —       |
| `ai_provider`         | `grok` / `gloo`   | `grok`  |
| `grok_api_key`        | xAI API key       | —       |
| `gloo_client_id`      | Gloo OAuth2 ID    | —       |
| `gloo_client_secret`  | Gloo OAuth2 secret (masked) | — |
| `gloo_tradition`      | e.g. `nazarene`, `evangelical` | — |

Configurable in admin Settings → Email Connector and AI Moderation sections.
Email fallback: unknown or misconfigured provider always falls back to SMTP.
AI fallback chain: Gloo (if configured) → Grok → fail-open (approve submission).

---

## Admin test suite (apps/admin)

83 tests across 10 files — run with `cd apps/admin && pnpm test`

| File                          | Tests | What it covers                        |
|-------------------------------|-------|---------------------------------------|
| tests/placeholder.test.ts     | 1     | Vitest smoke test                     |
| tests/stores/auth.test.ts     | 8     | Pinia auth store                      |
| tests/layouts/AdminLayout.test.ts | 8 | Sidebar, topbar, slot, sign-out       |
| tests/pages/DashboardPage.test.ts | 3 | Welcome page, quick-nav cards         |
| tests/pages/SermonsIndexPage.test.ts | 7 | Sermon list, badges, edit links    |
| tests/pages/SermonEditPage.test.ts  | 10 | Edit form, PATCH, feedback          |
| tests/pages/EventsIndexPage.test.ts | 7 | Event list, badges, edit links     |
| tests/pages/EventEditPage.test.ts   | 8 | Edit form, PATCH, feedback          |
| tests/pages/PrayerQueuePage.test.ts | 16 | Moderation queue, approve/reject    |
| tests/pages/SettingsPage.test.ts    | 15 | Prayer chain email, connector UI    |

**Important vitest gotcha:** `useRoute` is stubbed as a global in `tests/setup.ts`.
Components must NOT import from `#app` — use Nuxt auto-imports (no import statement).
Test files override with `vi.stubGlobal('useRoute', () => ({ params: { id: '...' } }))`.

---

## API test suite (apps/api)

Run with `cd apps/api && python -m pytest --tb=short`

- `tests/test_auth.py` — JWT verification, RBAC, profile lookup
- `tests/test_sermons.py` — Sermon CRUD endpoints (37 tests)
- `tests/test_events.py` — Event CRUD endpoints
- `tests/test_prayer_requests.py` — Prayer board endpoints (24 tests)
- `tests/test_site_config.py` — Site config CRUD endpoints
- `tests/test_connectors.py` — Connector ABCs, SMTP, MS365, registry (14 tests)
- `tests/test_rls_migration.py` — Contract tests verifying RLS migration SQL

**Important:** Uses `PyJWT` (not `python-jose`). Import as `import jwt` and
catch `jwt.exceptions.InvalidTokenError` (not `JWTError`).

---

## Known issues / tech debt

- Public website (Phase 2) still uses mock sermon/event data — wire to API in Phase 10
- Alembic migrations not yet stamped against existing Supabase tables (need `alembic stamp b2c3d4e5f6a7`)
- Logos sync not yet active (sermons exist in DB from prior manual work)
- Admin app is `ssr: false` (client-only SPA) — `@pinia/nuxt 0.11.3` required for Nuxt 4 compatibility
