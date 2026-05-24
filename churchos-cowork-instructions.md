# ChurchOS — Cowork Project Instructions

---

## 1. Project Overview

**ChurchOS** is an open-source, modular church management platform. It gives congregations a beautiful public website and a staff admin panel — running at near-zero cost on free cloud tiers. The initial deployment targets Libby Church of the Nazarene (libbynaz.org) and will serve as the prototype for future multi-church deployments.

This project lives in a GitHub monorepo and is built incrementally through documented phases. Every phase is a working, deployable state of the application.

---

## 2. Your Operating Principles

You are a senior full-stack engineer building this project from scratch. Follow these rules without exception:

### Test-Driven Development (TDD)
- **Always write a failing test before writing implementation code.**
- Tests live alongside their modules. No orphan test files.
- A phase is not complete until all tests pass.
- Use `pytest` for backend (FastAPI), `vitest` for frontend (Nuxt/Vue).

### Incremental & Verified
- Build one piece at a time. Verify it works before moving to the next.
- If something breaks, fix it before continuing. Never paper over failures.
- Each meaningful unit of work ends with: `git add → git commit → git push`.

### Explain Everything
- When you create a file, explain:
  1. What it does
  2. Why it exists at this layer of the stack
  3. How it connects to already-existing files
- Never create a file silently.

### Branch Discipline
- All feature work happens on a feature branch cut from `dev`.
- Branch naming: `feature/phase-1-repo-setup`, `feature/phase-2-supabase-auth`, etc.
- Completed phases get merged: `feature/... → dev → staging → main`.
- Never commit directly to `staging` or `main`.

---

## 3. Tech Stack

| Layer | Technology |
|---|---|
| Frontend (public + admin) | Nuxt 4, Vue 3 Composition API |
| Styling | Tailwind CSS v4 |
| Backend API | FastAPI (Python 3.12) |
| Database | PostgreSQL via Supabase |
| Auth | Supabase Auth (JWT, RBAC) |
| Cache / Rate limiting | Upstash Redis |
| Media storage | Backblaze B2 |
| Monorepo tooling | pnpm workspaces + Turborepo |
| CI/CD | GitHub Actions |
| Hosting (frontend) | Cloudflare Pages |
| Hosting (backend) | Railway.app |
| DNS / CDN / WAF | Cloudflare |
| AI (prayer moderation) | Gloo AI (primary) → Anthropic Claude (fallback) |

---

## 4. Repository Layout

```
churchos/                          ← monorepo root
├── apps/
│   ├── web/                       ← Public church website (Nuxt 4)
│   ├── admin/                     ← Staff/admin dashboard (Nuxt 4)
│   └── api/                       ← REST API (FastAPI)
│       ├── app/
│       │   ├── main.py
│       │   ├── models/
│       │   ├── routers/
│       │   ├── schemas/
│       │   ├── services/
│       │   └── dependencies/
│       ├── tests/
│       ├── alembic/
│       └── requirements.txt
├── packages/
│   ├── ui/                        ← Shared Vue component library
│   ├── types/                     ← Shared TypeScript definitions
│   ├── config/                    ← Tailwind design system tokens
│   ├── maps/                      ← Pluggable map component
│   └── office-info/               ← Service times, hours, contact info
├── docs/                          ← VitePress documentation
├── .github/
│   └── workflows/
│       ├── ci.yml
│       ├── deploy-staging.yml
│       └── deploy-production.yml
├── turbo.json
├── pnpm-workspace.yaml
├── version.json
└── CHANGELOG.md
```

---

## 5. Branch & Deployment Model

```
feature/* ──► dev ──► staging ──► main (production)
                │         │           │
                │         │           └── Cloudflare Pages (prod)
                │         │           └── Railway.app (prod API)
                │         └── Cloudflare Pages (staging)
                │         └── Railway.app (staging API)
                └── (local / PR checks only)
```

### Rules
- `main` — production. Protected. Requires passing CI + PR approval.
- `staging` — mirrors production config. Used for final QA before release.
- `dev` — integration branch. Feature branches merge here first.
- Feature branches — named `feature/phase-N-description` or `fix/short-description`.

### PR Flow
1. Open PR from `feature/*` into `dev`.
2. CI runs: lint, type-check, all tests.
3. Merge to `dev` (squash preferred).
4. When `dev` is stable, open PR `dev → staging` for QA review.
5. After QA sign-off, open PR `staging → main` to release.

---

## 6. CI/CD Pipelines

### `ci.yml` — runs on every PR
- `pnpm install`
- `turbo lint`
- `turbo type-check`
- `turbo test` (vitest + pytest)
- `turbo build` (smoke check)

### `deploy-staging.yml` — runs on push to `staging`
- Deploys frontend to Cloudflare Pages (staging project)
- Deploys API to Railway (staging service)
- Runs `alembic upgrade head` on staging DB

### `deploy-production.yml` — runs on push to `main`
- Same as staging pipeline but targets production services
- Posts deployment notification

---

## 7. Environment Variables

Each app has its own `.env.example`. Never commit `.env` files. All secrets live in:
- **Railway** — backend environment variables
- **Cloudflare Pages** — frontend environment variables
- **GitHub Actions Secrets** — CI/CD pipeline secrets

Key variable groups:

```bash
# Supabase
SUPABASE_URL=
SUPABASE_ANON_KEY=
SUPABASE_SERVICE_KEY=
SUPABASE_JWT_SECRET=
NUXT_PUBLIC_SUPABASE_URL=
NUXT_PUBLIC_SUPABASE_ANON_KEY=

# Redis
REDIS_URL=

# Backblaze B2
B2_KEY_ID=
B2_APPLICATION_KEY=
B2_BUCKET_NAME=

# AI providers
GLOO_CLIENT_ID=
GLOO_CLIENT_SECRET=
GLOO_TRADITION=evangelical
GLOO_PUBLISHER=
ANTHROPIC_API_KEY=

# App
CHURCH_SLUG=libby-naz
CHURCH_NAME=Libby Church of the Nazarene
```

---

## 8. Design System Summary

The design system lives in `packages/config/tailwind.config.ts`. All apps extend it.

### Colors
| Token | Hex | Role |
|---|---|---|
| `forest-500` | `#2d6a4f` | Primary brand, buttons |
| `forest-600` | `#23553f` | Hover states |
| `kootenai-500` | `#3a7d8c` | Secondary / accents |
| `charcoal-900` | `#0a1012` | Dark mode deepest surface |
| `stone-50` | `#faf8f5` | Light mode page background |
| `gold-500` | `#c9962b` | Accent, decorative elements |

### Fonts
- **Cinzel** — Display headings (h1, h2)
- **Lora** — Body copy, article content, scripture
- **DM Sans** — UI chrome, navigation, buttons

### Core Component Classes
`btn-primary`, `btn-secondary`, `btn-ghost`, `co-card`, `co-card-featured`, `co-container`, `co-section`, `scripture-callout`, `badge-forest`, `badge-kootenai`, `badge-gold`, `form-input`, `form-label`

Dark mode is enabled via `class` strategy with `@nuxtjs/color-mode`.

---

## 9. Security Requirements

Always enforce these — no exceptions:

- Access tokens in **memory only** — never `localStorage`
- Refresh tokens in **HttpOnly cookies** only
- JWT verified server-side on every protected endpoint
- RLS enabled on all sensitive Supabase tables
- PII encrypted at rest (AES-256, column-level)
- Rate limiting via Redis on all write endpoints
- Stripe.js handles card input — card data never hits our servers
- Prayer board submissions moderated by AI before going public
- Directory never publicly accessible — `member` role minimum
- No bulk export endpoint for the directory

### RBAC Roles
`superadmin → admin → staff → member → guest`

---

## 10. Phase Roadmap

See Section 11 for full phase definitions. Phases build on each other. Never skip.

| Phase | Name | Milestone |
|---|---|---|
| 0 | Repo & Tooling | Monorepo with CI passes |
| 1 | Design System | Tailwind tokens, fonts, base components |
| 2 | Public Website | Homepage, sermons, contact, about |
| 3 | Supabase Auth | Login, RBAC, JWT, RLS |
| 4 | Admin Dashboard | Staff panel, content management |
| 5 | Prayer Board | Moderated submissions, AI review |
| 6 | Gloo AI Integration | Prayer mod + "Ask Our Church" prep |
| 7 | Giving Module | Stripe integration, giving records |
| 8 | Member Directory | Consent-based, encrypted, member-only |
| 9 | Multi-Church | Church slug system, rebranding per church |
| 10 | Polish & Hardening | Audit, performance, documentation |

---

## 11. Phase Definitions

---

### Phase 0 — Repo & Tooling

**Goal:** A working monorepo with passing CI. Nothing runs yet except the scaffolding.

**Tasks:**
1. Initialize GitHub repo with `main`, `staging`, and `dev` branches.
2. Protect `main` and `staging` (require PR + passing CI).
3. Create `pnpm-workspace.yaml`, `turbo.json`, root `package.json`.
4. Scaffold `apps/web` (Nuxt 4), `apps/admin` (Nuxt 4), `apps/api` (FastAPI).
5. Add `packages/config`, `packages/ui`, `packages/types` stubs.
6. Configure `turbo.json` pipelines: `lint`, `build`, `test`, `type-check`.
7. Write `.github/workflows/ci.yml`.
8. Write `.github/workflows/deploy-staging.yml`.
9. Write `.github/workflows/deploy-production.yml`.
10. Add `.env.example` to each app.
11. Add `version.json` to repo root: `{ "version": "0.1.0" }`.
12. Write initial `CHANGELOG.md`.

**Tests to write first:**
- CI workflow: a trivial `apps/api` test that returns `True` (proves pytest runs).
- A trivial `apps/web` vitest test (proves frontend test runner works).
- CI must be green before phase is closed.

**Done when:** `git push origin dev` triggers CI and all checks pass.

---

### Phase 1 — Design System

**Goal:** The Tailwind design system is fully configured and documented. A shared UI component library has the core component set built and tested.

**Tasks:**
1. Build `packages/config/tailwind.config.ts` with the full color palette (forest, kootenai, charcoal, stone, gold), font families (Cinzel, Lora, DM Sans), and the `@layer components` utility classes.
2. Load Google Fonts in `apps/web` and `apps/admin`.
3. Build base components in `packages/ui`:
   - `CoButton` (all variants + sizes)
   - `CoCard` / `CoCardFeatured`
   - `CoContainer` / `CoSection`
   - `CoBadge`
   - `CoFormInput` / `CoFormLabel`
   - `ScriptureCallout`
   - `CoDivider`
4. Write component tests (Vitest + Vue Test Utils) for each component.
5. Configure dark mode (`class` strategy + `@nuxtjs/color-mode`).
6. Create a design system preview page at `/design-system` in `apps/web` (dev-only route).

**Done when:** All component tests pass; preview page renders correctly in both light and dark mode.

---

### Phase 2 — Public Website

**Goal:** The full public-facing church website is live and statically generated.

**Pages to build:**
- `/` — Homepage (hero, service times, map, brief about, recent sermons, contact CTA)
- `/about` — Church story, pastor bio, beliefs
- `/sermons` — Sermon archive with filters (series, speaker, date)
- `/sermons/[slug]` — Individual sermon page with audio/video player
- `/give` — Giving information + link to online giving
- `/contact` — Contact form, map embed, service times, address
- `/privacy` — Privacy policy
- `/404` — Custom not-found page

**Tasks:**
1. Build each page using the `packages/ui` component library.
2. Implement `packages/office-info` — service times, address, phone, email as config.
3. Implement `packages/maps` — pluggable map component (starts with Google Maps embed).
4. Wire sermon archive to static JSON data (real API comes in Phase 4).
5. Implement contact form (submits to `POST /api/v1/contact` — stubbed in Phase 4).
6. Configure Nuxt static generation for all public pages.
7. Ensure all pages pass Lighthouse score ≥ 95 (performance, accessibility).
8. Test responsiveness: mobile, tablet, desktop.

**Tests to write first:**
- Page rendering tests for each route (vitest + `@nuxt/test-utils`).
- Accessibility tests (no missing alt text, correct heading hierarchy).

**Done when:** `pnpm build` generates static HTML; all pages render; Lighthouse ≥ 95.

---

### Phase 3 — Supabase Auth & Database

**Goal:** Users can log in. The database is live. RLS is active on sensitive tables.

**Tasks:**
1. Set up Supabase project (document the steps in `docs/deploy-supabase.md`).
2. Write Alembic migrations for core tables:
   - `churches` (id, name, slug, config JSONB)
   - `users` (id, church_id, email, role, created_at)
   - `sermons` (id, church_id, title, slug, speaker, series, date, audio_url, video_url, description)
   - `events` (id, church_id, title, date, description, location)
3. Enable RLS on `users` table; write policies.
4. Implement FastAPI auth dependencies:
   - `get_current_user` — validates Supabase JWT
   - `require_role(role)` — enforces RBAC
5. Implement login flow in `apps/admin`:
   - Login page → Supabase Auth → JWT stored in memory → refresh token in HttpOnly cookie
6. Protect all `/admin/*` routes with auth middleware.
7. Implement logout (invalidate refresh token).

**Tests to write first:**
- `test_auth.py` — test JWT validation, invalid token rejection, expired token handling.
- `test_rbac.py` — test that each role can/cannot access protected endpoints.
- Frontend: login form renders, error state on bad credentials.

**Done when:** Admin login works end-to-end; unauthorized access to `/admin` redirects to login; all auth tests pass.

---

### Phase 4 — Admin Dashboard & Content Management

**Goal:** Staff can log in and manage sermons, events, and church info through a clean admin interface.

**Admin pages:**
- `/admin` — Dashboard (quick stats: upcoming events, recent sermons, prayer count)
- `/admin/sermons` — Sermon list + create/edit/delete
- `/admin/sermons/[id]` — Sermon editor (title, speaker, series, date, audio upload, description)
- `/admin/events` — Event list + create/edit/delete
- `/admin/settings` — Church info (name, service times, address, contact info)
- `/admin/users` — User list (admin only); promote/demote roles

**Tasks:**
1. Build admin layout: sidebar nav, topbar with church name + version badge + user menu.
2. Implement CRUD API endpoints for sermons and events.
3. Wire sermon and event editors to the API.
4. Implement Backblaze B2 upload for sermon audio/video.
5. Wire the public `/sermons` page to the live API (replace static JSON).
6. Wire the contact form to `POST /api/v1/contact` (email via Resend or similar).

**Tests to write first:**
- `test_sermons.py` — CRUD operations, slug uniqueness, auth required.
- `test_events.py` — CRUD operations, past/future filtering.
- Admin UI: sermon list loads, editor saves correctly.

**Done when:** Staff can create, edit, and delete a sermon; it appears on the public site immediately.

---

### Phase 5 — Prayer Board

**Goal:** Visitors can submit prayer requests; staff moderate them; approved requests appear publicly.

**Tasks:**
1. Add `prayer_requests` table migration:
   - `id`, `church_id`, `content`, `submitter_email` (encrypted), `status` (pending/approved/rejected), `ai_moderation_result`, `created_at`
2. Implement `POST /api/v1/prayer` endpoint:
   - Validate input (Pydantic)
   - Rate limit: 3/hour per IP (Redis)
   - Submit to AI moderation (returns immediately; moderation is async)
3. Implement AI moderation service (`app/services/ai_provider.py`):
   - Check `GLOO_*` env vars → use Gloo if present
   - Else check `ANTHROPIC_API_KEY` → use Claude Haiku
   - Else → mark as `pending_manual`
4. Implement `GET /api/v1/prayer` — returns approved requests (paginated, no email exposed).
5. Build public prayer board page at `/prayer`.
6. Build admin prayer moderation queue at `/admin/prayer`.

**Tests to write first:**
- `test_prayer.py` — submission, rate limiting, moderation routing, status transitions.
- `test_ai_provider.py` — mock both providers; test fallback logic.
- Public board: only approved requests shown.

**Done when:** Submission → AI review → approved request appears on public board. Rate limiting enforced.

---

### Phase 6 — Gloo AI Integration

**Goal:** Gloo AI is the primary AI provider, fully integrated. Foundation for "Ask Our Church" chatbot is laid.

**Tasks:**
1. Build `app/services/gloo.py` — full Gloo API client:
   - OAuth token exchange (client credentials flow)
   - Completions with `tradition` parameter
   - Grounded Completions (RAG over publisher content)
2. Build `app/services/anthropic_fallback.py` — thin Anthropic wrapper.
3. Build `app/services/ai_provider.py` — provider router (Gloo → Anthropic → manual).
4. Implement provider priority logic (see Gloo AI guide).
5. Document Gloo publisher setup in admin settings.
6. Add `/admin/settings/ai` page — shows active provider, tradition setting, publisher name.
7. Lay foundation for "Ask Our Church" chatbot endpoint: `POST /api/v1/ask` (returns 501 Not Implemented until Phase content is uploaded).

**Tests to write first:**
- `test_gloo_client.py` — mock Gloo API; test token refresh, tradition param, grounded completions.
- `test_ai_provider.py` — test fallback chain; Gloo down → falls to Anthropic → falls to manual.

**Done when:** Prayer board uses Gloo in staging. Provider can be switched via `.env` with no code changes.

---

### Phase 7 — Giving Module

**Goal:** Visitors can give online. Admins can see giving totals. Members can see their own giving history.

**Tasks:**
1. Add `giving_records` table migration:
   - `id`, `church_id`, `user_id` (nullable for guest), `stripe_payment_intent_id`, `amount_cents`, `fund`, `created_at`
2. Implement Stripe integration:
   - `POST /api/v1/giving/intent` — creates a Stripe PaymentIntent; returns `client_secret`
   - `POST /api/v1/giving/webhook` — handles Stripe webhooks; records successful payments
3. Build public giving page — uses Stripe.js for card input (no card data touches our server).
4. Build `/admin/giving` — totals by fund, recent transactions, exportable CSV (admin only).
5. Build `/admin/members/[id]/giving` — member's own giving history.

**Security requirements for this phase:**
- Stripe.js handles all card input.
- Webhook endpoint validates Stripe signature.
- Giving records are member-only — users can only see their own.

**Tests to write first:**
- `test_giving.py` — intent creation, webhook handling, signature validation, access control.
- No card data appears in API logs or responses.

**Done when:** A test donation completes in Stripe test mode; record appears in admin dashboard.

---

### Phase 8 — Member Directory

**Goal:** Opted-in members can see a church directory. Each member controls exactly what they share.

**Tasks:**
1. Add `members` table migration:
   - `id`, `church_id`, `user_id`, `display_name`, `email_encrypted`, `phone_encrypted`, `address_encrypted`, `show_email`, `show_phone`, `show_address`, `photo_url`, `joined_at`
2. Implement column-level encryption (AES-256) for PII fields.
3. Implement directory API:
   - `GET /api/v1/directory` — requires `member` role; returns only opted-in fields; paginated; rate limited.
   - No bulk export endpoint.
4. Implement audit log for every directory access.
5. Build member profile editor at `/admin/profile` — member controls their own visibility.
6. Build directory page at `/members/directory` — requires login.
7. Add admin directory management at `/admin/members`.

**Tests to write first:**
- `test_directory.py` — access control (guest blocked, member allowed), field masking (respects show_* flags), audit log written, no bulk export possible.

**Done when:** A member can log in, set their visibility, and appear in the directory to other members.

---

### Phase 9 — Multi-Church Support

**Goal:** A second church can be deployed from the same codebase with a different `CHURCH_SLUG` and design tokens.

**Tasks:**
1. Confirm all queries are scoped by `church_id`.
2. Implement church config JSONB — stores name, slug, service times, contact info, design overrides per church.
3. Update `packages/config` to support per-church color overrides via CSS custom properties.
4. Document the rebranding process in `docs/new-church-setup.md`.
5. Test with a mock second church in staging.

**Done when:** Changing `CHURCH_SLUG` in `.env` and updating design tokens produces a fully rebranded instance with no data crossover.

---

### Phase 10 — Polish, Hardening & Documentation

**Goal:** The system is production-hardened, fully documented, and ready for other churches to adopt.

**Tasks:**
1. Full security audit:
   - Review all RLS policies.
   - Run `pip-audit` and `pnpm audit`; patch findings.
   - Penetration test auth endpoints.
2. Performance:
   - Lighthouse ≥ 95 on all public pages.
   - Core Web Vitals passing.
   - API response time < 200ms on P95.
3. Sentry integration — error tracking for both Nuxt apps and FastAPI.
4. Uptime monitoring (Better Uptime or similar — free tier).
5. Complete the user guide (see Section 12).
6. Write `docs/new-church-setup.md` — full guide for adopting churches.
7. Tag release `1.0.0 "Kootenai"` in GitHub.
8. Write full `CHANGELOG.md` entry for `1.0.0`.

---

## 12. Versioning

ChurchOS uses Semantic Versioning (MAJOR.MINOR.PATCH).

| Version bump | When |
|---|---|
| PATCH | Bug fixes, security patches |
| MINOR | New backward-compatible module |
| MAJOR | Breaking changes, schema migrations requiring manual steps |

Release codenames follow Kootenai River Valley geography:
`1.0.0 Kootenai → 1.1.0 Cabinet → 1.2.0 Fisher → 1.3.0 Quartz → 2.0.0 Yaak`

Current version is always visible in:
- The site footer
- The admin topbar badge (top-right)
- `GET /health` API response: `{ "status": "ok", "version": "1.0.0" }`
- `version.json` in the repo root

---

## 13. Hosting Architecture (Production)

```
Internet
    │
    ▼
Cloudflare (DNS + CDN + WAF — free)
    │
    ├── libbynaz.org ────────► Cloudflare Pages (Nuxt web — free)
    ├── admin.libbynaz.org ──► Cloudflare Pages (Nuxt admin — free)
    └── api.libbynaz.org ────► Railway.app (FastAPI — free tier)
                                    │
                                    ├── Supabase (PostgreSQL + Auth — free)
                                    ├── Upstash Redis (rate limiting — free)
                                    └── Backblaze B2 (media — ~free)
```

**Estimated monthly cost:** $0–$5 for a small congregation.

---

## 14. Useful Commands

```bash
# Install all dependencies
pnpm install

# Run all apps in dev mode
pnpm dev

# Run all tests
pnpm test

# Build everything
pnpm build

# Run backend tests only
cd apps/api && pytest

# Run frontend tests only
cd apps/web && pnpm test

# Apply database migrations
cd apps/api && alembic upgrade head

# Check current version
cat version.json

# Check API health (production)
curl https://api.libbynaz.org/health
```

---

*ChurchOS — built for the congregation, owned by the congregation.*
