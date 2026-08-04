# ChurchOS — CLAUDE.md

Project context and conventions for AI-assisted development.
**This file is the single source of truth for any new session.**

Companion docs: [PLAN.md](PLAN.md) (phase roadmap) ·
[DEVELOPER-GUIDE.md](DEVELOPER-GUIDE.md) (how-to detail) ·
[CHANGELOG.md](CHANGELOG.md) (what shipped) ·
[churchos-user-guide.md](churchos-user-guide.md) (end-user docs)

---

## What this is

ChurchOS is a modular, open-source church CMS built for Libby Church of the Nazarene
and designed for multi-church deployment. It replaces the active church website.

**Version:** 0.1.0 pre-release — Release 1.0.0 is named "Kootenai"

---

## Stack

| Layer        | Technology                                      |
|--------------|-------------------------------------------------|
| Frontend     | Nuxt 4, Vue 3 Composition API, Tailwind CSS v4  |
| Backend      | FastAPI (Python 3.12), Supabase (PostgreSQL)    |
| Auth         | Supabase Auth, JWT (PyJWT), RBAC                |
| Monorepo     | pnpm workspaces + Turborepo                     |
| CI           | GitHub Actions                                  |
| Frontend CD  | Cloudflare Pages                                |
| Backend CD   | Railway.app                                     |
| DNS/CDN/WAF  | Cloudflare                                      |
| Cache        | Upstash Redis                                   |
| Storage      | Backblaze B2 (planned — not yet implemented)    |

---

## Monorepo structure

```
apps/
  web/      — Public-facing Nuxt 4 site (homepage, sermons, events, prayer, contact)
  admin/    — Admin dashboard Nuxt 4 app (CRUD, content management)
  api/      — FastAPI backend (app/, tests/, alembic/, requirements.txt)
packages/
  ui/       — Shared Vue component library
  config/   — Design tokens + shared component CSS
  types/    — Shared TypeScript definitions
docs/       — Documentation assets
```

`packages/maps` and `packages/office-info` appear in older planning docs but do
not exist yet — do not reference them as if they do.

---

## Non-negotiable rules

- **TDD always.** Write a failing test before any implementation. No exceptions.
  `pytest` for the API, `vitest` for the Nuxt apps and `packages/ui`. Tests live
  alongside the module they cover — no orphan test files.
- **Explain every file.** What it does, why it exists, how it connects. Never
  create a file silently.
- **Incremental and verified.** One piece at a time, confirm it works, then move
  on. If something breaks, fix it — never paper over a failure.
- **Commit often.** git add → commit → push after each meaningful working unit.
- **Docs move in step with code.** Any change that alters behavior, schema,
  commands, or env vars updates CHANGELOG.md (`## [Unreleased]`) in the same PR.

---

## Commands

All verified working from the repo root unless noted.

```bash
pnpm install                          # install all workspace deps
pnpm dev                              # run all apps (web :3000, admin :3001, api :8000)
pnpm build                            # turbo build
pnpm lint                             # turbo lint
pnpm type-check --filter='!@churchos/api'   # see caveat below
pnpm test --filter='!@churchos/api'         # vitest across web, admin, ui
```

**Caveat — the bare root `type-check` and `test` tasks fail.** Turbo includes
`@churchos/api`, whose scripts shell out to `mypy` and `pytest`; neither is on
`PATH` outside the Python venv, and `mypy` is not in `requirements.txt` at all.
CI works around this the same way (`--filter=!@churchos/api` in
[ci.yml](.github/workflows/ci.yml)). Run the Python side directly instead:

```bash
cd apps/api
source .venv/bin/activate
pytest --tb=short                     # 137 tests
ruff check .                          # lint
alembic upgrade head                  # apply migrations
```

Other useful commands:

```bash
cat version.json                                          # current version
curl https://churchos-production-c6ae.up.railway.app/health   # prod API health
```

> Note: the root script is `pnpm type-check` (hyphenated). `pnpm typecheck`
> does not exist.

---

## Environment variables

Never commit a `.env` file. Secrets live in **Railway** (API), **Cloudflare
Pages** (web/admin), and **GitHub Actions Secrets** (CI/CD). Each app has a
`.env.example` documenting its real variable names.

### `apps/api` — read by [app/config.py](apps/api/app/config.py)

| Variable | Required | Notes |
|---|---|---|
| `SUPABASE_URL` | yes | Project REST URL |
| `SUPABASE_SERVICE_KEY` | yes | Supabase **secret key** (formerly service_role) — bypasses RLS, server only |
| `SUPABASE_JWT_SECRET` | yes | Settings → API → JWT Settings; verifies HS256 access tokens |
| `CHURCH_ID` | yes | `default` — the singleton row id in `public.churches` |
| `CHURCH_SLUG` | no | defaults to `libby-naz` |
| `UPSTASH_REDIS_URL` | no | rate limiting; fail-open when blank |
| `UPSTASH_REDIS_TOKEN` | no | Upstash REST token used as Redis AUTH password |
| `GROK_API_KEY` | no | xAI moderation fallback; fail-open when blank |
| `ANTHROPIC_API_KEY` | no | declared but currently unused |
| `SMTP_HOST` / `SMTP_PORT` / `SMTP_USER` / `SMTP_PASSWORD` / `SMTP_FROM_NAME` | no | default SMTP email connector; port defaults `587`, name defaults `ChurchOS` |
| `DATABASE_URL` | migrations only | read by [alembic/env.py](apps/api/alembic/env.py), not by `config.py`; use the non-pooled URI |

### `apps/web` — read by [nuxt.config.ts](apps/web/nuxt.config.ts)

| Variable | Notes |
|---|---|
| `NUXT_PUBLIC_API_BASE` | API origin; falls back to the Railway production URL |

### `apps/admin` — read by [nuxt.config.ts](apps/admin/nuxt.config.ts)

| Variable | Notes |
|---|---|
| `NUXT_PUBLIC_SUPABASE_URL` | Supabase project URL |
| `NUXT_PUBLIC_SUPABASE_ANON_KEY` | Supabase **publishable key** (formerly anon) |

> **Not env-driven:** connector credentials (MS365, Gloo, Grok provider keys)
> are stored in the `site_config` table and edited in admin Settings — see
> [Connector framework](#connector-framework-phases-67). Backblaze B2 keys
> appear in older docs but nothing reads them yet.

> **Supabase naming (2025):** "publishable" = old anon key, "secret" = old
> service_role key.

---

## Git workflow

- `feature/*` branches cut from `dev`
- Merge path: `feature/*` → `dev` → `staging` → `main`
- `main`, `staging`, `dev` are protected — PRs only, CI must pass
- Never commit directly to `staging` or `main`
- Branch naming: `feature/phase-N-description` or `fix/short-description`

### PR flow

1. Open PR from `feature/*` into `dev`; CI runs lint, type-check, build, tests.
2. Merge to `dev` (squash preferred).
3. When `dev` is stable, open `dev → staging` for QA.
4. After QA sign-off, open `staging → main` to release.

### CI/CD

| Workflow | Trigger | Does |
|---|---|---|
| `ci.yml` | PR into dev/staging/main, push to dev | turbo lint · type-check · build · vitest (all `--filter=!@churchos/api`), then a separate Python job: `ruff check .` + `pytest --tb=short` |
| `deploy-staging.yml` | push to `staging` | builds `apps/web` → Cloudflare Pages project `churchos-staging`. Railway staging step is a no-op — that environment is not configured yet. |
| `deploy-production.yml` | push to `main` | builds `apps/web` → Cloudflare Pages project `churchos`; `railway up --service churchos`; posts a deploy notification |

**What CD does *not* do yet:** `apps/admin` is never built or deployed by any
workflow, and the `alembic upgrade head` step is commented out in both deploy
files — migrations are applied by hand. Do not assume a merge to `main` migrates
the database.

---

## Versioning

Semantic versioning (MAJOR.MINOR.PATCH). PATCH = fixes/security; MINOR = new
backward-compatible module; MAJOR = breaking changes or migrations needing
manual steps.

Release codenames follow Kootenai River Valley geography:
`1.0.0 Kootenai → 1.1.0 Cabinet → 1.2.0 Fisher → 1.3.0 Quartz → 2.0.0 Yaak`

The current version must stay in sync across: `version.json` (root) · the site
footer · the admin topbar badge · `GET /health`.

---

## RBAC roles

`superadmin → admin → staff → member → guest`

Enforced in [apps/api/app/dependencies/rbac.py](apps/api/app/dependencies/rbac.py)
via `require_role()`.

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

**Tokens are authoritative in [packages/config/src/tokens.css](packages/config/src/tokens.css)**
— a Tailwind v4 CSS-first `@theme` block. Do not duplicate hex values into docs
or app code; read them from that file.

- **Palette scales:** `forest` (primary green, 50–900), `kootenai` (secondary
  teal, 50–900), `gold` (accent, 50–900), `charcoal` (dark surfaces, 700–900),
  `stone` (light surfaces, 50–200). Colours are drawn from the Kootenai River
  Valley — forest canopy, river teal, stained-glass gold, warm river stone.
- **Fonts:** `--font-display` Cinzel (h1/h2) · `--font-body` Lora (body copy,
  scripture) · `--font-ui` DM Sans (nav, buttons, labels). Loaded from Google
  Fonts in each app's `nuxt.config.ts`.
- **Dark mode:** class strategy via `@nuxtjs/color-mode`. Tailwind v4 needs the
  explicit `@variant dark (&:where(.dark, .dark *));` override in each app's
  `main.css`, otherwise `dark:` utilities follow the OS media query instead of
  the `.dark` class.

**Component classes** live in
[packages/config/src/components.css](packages/config/src/components.css) — 13
classes currently implemented:

`btn-primary` · `btn-secondary` · `btn-ghost` · `co-card` · `co-card-featured` ·
`co-container` · `co-section` · `scripture-callout` · `badge-forest` ·
`badge-kootenai` · `badge-gold` · `form-input` · `form-label`

Live reference page: `/design` in `apps/web`
([app/pages/design.vue](apps/web/app/pages/design.vue)), `noindex`.

Rebranding for another church = editing `tokens.css` only.

> **Known drift:** [packages/config/tailwind.config.ts](packages/config/tailwind.config.ts)
> is a Phase 0 stub that restates the same palette but is **not consumed** by
> either app — both use the CSS-first `@import "@churchos/config/tokens.css"`
> path. Treat `tokens.css` as the only source of truth. Design docs circulating
> outside the repo also describe classes that do not exist yet (`co-divider`,
> `co-section-label/title/subtitle`, `co-section-sm`, `btn-outline-light`,
> `btn-sm/md/lg/xl`, `text-gradient-brand`, `accent-border-left`) — treat those
> as unbuilt.

---

## Deployed infrastructure

| Service         | URL / Location                                           |
|-----------------|----------------------------------------------------------|
| API (prod)      | https://churchos-production-c6ae.up.railway.app          |
| Public site     | Cloudflare Pages — `churchos` project                    |
| Public site (staging) | Cloudflare Pages — `churchos-staging` project      |
| Admin           | Not deployed yet — no CD workflow builds `apps/admin`    |
| Supabase        | churchos-libbynaz project                                |

Target production topology: Cloudflare fronts everything —
`libbynaz.org` → Pages (web), `admin.libbynaz.org` → Pages (admin),
`api.libbynaz.org` → Railway (FastAPI) → Supabase + Upstash + B2.
Running cost is $0–5/month on free tiers.

---

## Deployment architecture (important)

ChurchOS is a **single-tenant, portable CMS**. Each church gets its own isolated
deployment — their own Supabase project, Railway service, and Cloudflare account.
There is no shared database and no cross-church data isolation needed in code.

"Multi-church support" means **portability and easy self-hosting**, not
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

**Active providers** are set in the `site_config` table:

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

## Test suites

### `apps/api` — 137 tests

`cd apps/api && source .venv/bin/activate && pytest --tb=short`

| File | Tests | Covers |
|---|---|---|
| tests/test_prayer_requests.py | 24 | Prayer board endpoints |
| tests/test_ai_connectors.py   | 20 | Grok, Gloo, fallback chain, moderation dependency |
| tests/test_events.py          | 19 | Event CRUD |
| tests/test_sermons.py         | 18 | Sermon CRUD |
| tests/test_rls_migration.py   | 17 | Contract tests over RLS migration SQL |
| tests/test_connectors.py      | 14 | Email ABCs, SMTP, MS365, registry |
| tests/test_site_config.py     | 11 | Site config CRUD |
| tests/test_auth.py            | 7  | JWT verification, RBAC |
| tests/test_health.py          | 4  | `/health` + version |
| tests/test_get_profile.py     | 3  | Profile lookup |

**Important:** uses `PyJWT`, not `python-jose`. Import as `import jwt` and catch
`jwt.exceptions.InvalidTokenError` (not `JWTError`).

### `apps/admin` — 91 tests across 10 files

`cd apps/admin && pnpm test`

| File | Tests | Covers |
|---|---|---|
| tests/pages/SettingsPage.test.ts     | 23 | Prayer chain email, connector UI |
| tests/pages/PrayerQueuePage.test.ts  | 16 | Moderation queue, approve/reject |
| tests/pages/SermonEditPage.test.ts   | 10 | Edit form, PATCH, feedback |
| tests/layouts/AdminLayout.test.ts    | 8  | Sidebar, topbar, slot, sign-out |
| tests/pages/EventEditPage.test.ts    | 8  | Edit form, PATCH, feedback |
| tests/stores/auth.test.ts            | 8  | Pinia auth store |
| tests/pages/EventsIndexPage.test.ts  | 7  | Event list, badges, edit links |
| tests/pages/SermonsIndexPage.test.ts | 7  | Sermon list, badges, edit links |
| tests/pages/DashboardPage.test.ts    | 3  | Welcome page, quick-nav cards |
| tests/placeholder.test.ts            | 1  | Vitest smoke test |

**Important vitest gotcha:** `useRoute` is stubbed as a global in
`tests/setup.ts`. Components must NOT import from `#app` — use Nuxt auto-imports
(no import statement). Test files override with
`vi.stubGlobal('useRoute', () => ({ params: { id: '...' } }))`.

### `apps/web` — 53 tests · `packages/ui` — 33 tests

`pnpm test --filter=@churchos/web` / `--filter=@churchos/ui`

---

## Phase status

Full roadmap and per-phase done-criteria live in [PLAN.md](PLAN.md).
Phases 0–7 are complete; **Phase 8 (Giving module, Stripe) is next.**

---

## Known issues / tech debt

- Root `pnpm type-check` and `pnpm test` fail on `@churchos/api` — `mypy` is not
  in `requirements.txt`, and both scripts assume the venv is on `PATH`. CI dodges
  it with `--filter=!@churchos/api`. Fix by adding `mypy` and running the Python
  tasks through the venv, or by dropping the api workspace from the turbo tasks.
- Public website (Phase 2) still uses mock sermon/event data — wire to API in Phase 12
- Alembic migrations not yet stamped against existing Supabase tables (need `alembic stamp b2c3d4e5f6a7`)
- Logos sync not yet active (sermons exist in DB from prior manual work)
- Admin app is `ssr: false` (client-only SPA) — `@pinia/nuxt 0.11.3` required for Nuxt 4 compatibility
- `packages/config/tailwind.config.ts` duplicates `tokens.css` but is unused — see Design system
- Backblaze B2 is documented as the storage layer but no code reads B2 credentials yet
