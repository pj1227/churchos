# ChurchOS — Master Build Plan

> **Status: DRAFT — awaiting owner review** · Drafted 2026-10-07 on `docs/replan`
> This plan replaces the FastAPI + Supabase plan, which is preserved at git tag
> [`archive/fastapi-0.x`](https://github.com/pj1227/churchos/tree/archive/fastapi-0.x).
> Items marked **⚖ Decision** need your approval before the phase that depends on them starts.

This file owns the **roadmap**: what each phase delivers and when it is done.
[CLAUDE.md](CLAUDE.md) owns **how we work** (workflow, standards, security rules).
[docs/design/DOMAIN-MODEL.md](docs/design/DOMAIN-MODEL.md) owns **what the data looks like**.
None of the three restates the others.

---

## 1. Direction

ChurchOS is a modular, open-source church CMS. It is built first for Libby Church
of the Nazarene, where it replaces https://libbynaz.org, and is designed so any
church can self-host it on inexpensive shared hosting.

| Principle | What it means in practice |
|---|---|
| **Cheap hosting first** | The reference deployment is cPanel shared hosting (PHP + MariaDB). Nothing may require a long-running process, Node on the server, or a paid platform. |
| **Native libraries first** | Each language gets a plain core library (PHP, TypeScript, later Python) with no framework dependency. Framework code (Laravel, Nuxt, later FastAPI) is a thin adapter on top. |
| **One domain model** | Every backend and frontend implements [DOMAIN-MODEL.md](docs/design/DOMAIN-MODEL.md). JSON Schemas enforce it, and contract tests check every backend over HTTP. |
| **Modules** | Features ship as modules that an admin enables and configures. Every module includes its own admin screens. |
| **Vertical slices** | A phase delivers one feature through every layer: contract → core → API → admin → public site → deploy. No phase leaves "wire it up later" work. |
| **Done means live** | A phase is done only when it is running in production, after verification on test. |

---

## 2. Architecture at a glance

### Repository layout (target — ⚖ Decision D1)

```
churchos/
├── apps/
│   ├── web/                  Nuxt — public site (statically generated)
│   ├── admin/                Nuxt — admin dashboard (static SPA)
│   └── api-laravel/          Laravel — REST API (thin adapter over the PHP core)
│   # later: api-fastapi/ (restored from archive/fastapi-0.x), other frontends
├── libs/
│   ├── shared/
│   │   └── contract/         JSON Schemas + openapi.yaml (enforces the domain model)
│   ├── php/
│   │   └── churchos-core/    Plain PHP: domain objects, ports, services, source adapters
│   └── ts/
│       ├── churchos-core/    Plain TS: generated types, API client
│       ├── ui/               Vue components (plain Vue, no Nuxt)
│       └── theme/            Design tokens (CSS) + component CSS
├── e2e/                      Browser tests against a real running stack
├── docs/                     design/, guides, assets
├── .github/workflows/
├── turbo.json · pnpm-workspace.yaml · version.json · CHANGELOG.md
```

- `libs/<lang>/` keeps the per-language cores side by side, so adding Python later is
  `libs/python/churchos-core` + `apps/api-fastapi`.
- PHP packages are managed by Composer. Each one also gets a small `package.json`
  so Turborepo can run its lint and test tasks with everything else.

### Environments

| Env | Where | Deployed from | Purpose |
|---|---|---|---|
| dev | `localhost` | your working branch | Development; full stack runs locally |
| test | `test.libbynaz.org` | `staging` branch (automatic) | Release candidate; you verify in the UI here |
| prod | `libbynaz.org` | `main` branch (automatic) | Live site |

### Hosting topology (Namecheap Stellar Business — ⚖ Decision D2)

One domain per environment serves all three apps, so there is no cross-origin
setup and login cookies work simply:

| Path | Serves |
|---|---|
| `/` | `apps/web` static build |
| `/admin` | `apps/admin` static build |
| `/api` | Laravel (its `public/` entry point only) |

- Laravel code lives **outside** `public_html`; only its entry point is exposed.
- Deploys are **atomic**: GitHub Actions builds, uploads a new release directory over
  SSH, runs `php artisan migrate --force`, switches a `current` symlink, checks
  `/api/health`, and rolls back if that fails.
- Background work runs from **one cPanel cron entry** (every minute) that invokes
  the ChurchOS scheduler. The scheduler decides what is actually due (see Phase 6).
- Host facts recorded 2026-10-07: PHP selector offers 8.2–8.5 (currently 8.1, EOL;
  target **8.4**); MariaDB **11.4.13** (server charset `latin1` — we force `utf8mb4`);
  `pdo_mysql` and `pdo_pgsql` available; SSH available.

### Release model

```
feature/phase-N-* ──► dev ──(release PR, every 2 weeks)──► staging ──(after UI sign-off)──► main
                       CI only                             test.libbynaz.org              libbynaz.org + git tag
```

- **Cadence (⚖ Decision D3): two weeks.** Work that isn't ready waits for the next release.
- Unfinished modules may ship to production **disabled**. The module switch doubles
  as a feature flag.
- Hotfixes: `fix/*` from `main` → `main`, then merged back into `staging` and `dev`.

### Versioning (⚖ Decision D4)

Semantic versioning with Kootenai River Valley codenames per minor release.

| Version | Codename | Delivered by |
|---|---|---|
| 0.1.0 – 0.3.x | — (pre-release) | Phases 1–3 (not public; the old site stays live) |
| **1.0.0** | **Kootenai** | Phase 4 — the cutover that replaces libbynaz.org |
| 1.1.0 | Cabinet | Phase 5 — Prayer board |
| 1.2.0 | Fisher | Phase 6 — Scheduled tasks + Sermons |
| 1.3.0 | Quartz | Phase 7 — Events |
| 1.4.0+ | TBD (suggestions: Purcell, Koocanusa, Libby Creek, Kootenai Falls) | Phases 8+ |
| 2.0.0 | Yaak | Reserved for the first breaking change |

`version.json` is the single source. The site footer, admin badge and `GET /api/health`
read it at build or run time. They never hardcode it, which was a defect in the archived build.

---

## 3. Module system

A **module** is a self-contained feature bundle:

| Part | Example (Sermons) |
|---|---|
| Domain objects (in DOMAIN-MODEL.md) | `Sermon`, `SermonSeries` |
| Storage (migrations) | `sermons`, `sermon_series` tables |
| API routes | `GET /api/sermons`, `PATCH /api/admin/sermons/{id}` |
| Admin screens | Sermon list, edit, sync status |
| Public pages / blocks | `/sermons`, `/sermons/{slug}`, "Latest sermon" block |
| Settings (typed, validated) | source = `logos`, channel ID = `13608627`, sync schedule |
| Permissions | who may view and edit, by role |
| Scheduled task types | `sermons.sync` |

- Modules ship **inside this repo**. They are switched on per deployment, not
  installed from a marketplace. That avoids the security risk of third-party
  plugins and keeps this simpler than Drupal.
- **System modules** are always on (users & roles, site settings, scheduled tasks).
  **Feature modules** can be toggled (prayer, sermons, events, …).
- The module manifest and settings are domain objects (DOMAIN-MODEL §5), so every
  backend implements them the same way.

---

## 4. How every phase runs

The rules live in [CLAUDE.md → Workflow](CLAUDE.md#workflow-non-negotiable). The sequence:

1. **Plan review.** The phase section below is expanded into a detailed plan
   (domain objects, endpoints, screens, tests, dependencies) and presented for review.
2. **Docs first.** Agreed changes are applied to PLAN.md, DOMAIN-MODEL.md and the
   contract schemas, then merged.
3. **Branch + failing tests.** `feature/phase-N-*` is created. Tests (unit, contract,
   end-to-end) are shown, explained, approved, written, and committed failing.
4. **Build in reviewed steps.** Each piece of code is shown and explained before it is
   written, then made to pass its tests.
5. **CI green → `dev`.**
6. **Release to test** on the next release. You verify in the UI on test.libbynaz.org.
7. **Release to prod.** Tag, update CHANGELOG, mark the phase ✅.

---

## 5. Phase index

| # | Phase | Version | Status |
|---|---|---|---|
| 0 | Archive & re-plan | — | 🔄 in progress |
| 1 | Foundation: tooling, CI/CD, hosting | 0.1.0 | 🔲 |
| 2 | Design system (theme restoration) | 0.2.0 | 🔲 |
| 3 | Core platform: auth, users, settings, modules | 0.3.0 | 🔲 |
| 4 | Site content & cutover | **1.0.0 Kootenai** | 🔲 |
| 5 | Prayer board module | 1.1.0 Cabinet | 🔲 |
| 6 | Scheduled tasks + Sermons module | 1.2.0 Fisher | 🔲 |
| 7 | Events module | 1.3.0 Quartz | 🔲 |
| 8 | Giving module | 1.4.0 | 🔲 |
| 9 | Member directory module | 1.5.0 | 🔲 |
| 10 | External login providers | 1.6.0 | 🔲 |
| 11 | Integrations | 1.7.0 | 🔲 |
| 12 | Portability & second backend | 1.8.0 | 🔲 |

Phases 6 and 7 may swap if a temporary sermon embed (Phase 4) covers sermons long
enough. Phases 8–12 are outlines and will be planned in detail when they come up.

---

## Phase 0 — Archive & re-plan

**Goal:** Preserve the FastAPI build and agree the new plan before any code.

- [x] Push all unpushed branches; tag `archive/fastapi-0.x` at `main` (2026-10-07)
- [ ] Owner reviews and approves PLAN.md, CLAUDE.md, DOMAIN-MODEL.md drafts
- [ ] Decisions D1–D9 resolved and recorded in §Decisions
- [ ] `docs/replan` merged to `dev`

---

## Phase 1 — Foundation: tooling, CI/CD, hosting → 0.1.0

**Goal:** An empty but real system deployed to test and prod by CI, which proves
every pipe end to end: `GET /api/health` answers on libbynaz.org from Laravel via
the PHP core, and an `/admin` placeholder reads it.

**Repo**
- Clear the FastAPI-era app code from the working tree (it stays in the archive tag — ⚖ D5)
- Scaffold the target layout (§2): pnpm + Turborepo + Composer workspaces
- Formatters, linters and static analysis per language (CLAUDE.md → Coding standards); CI fails on violations
- `version.json` read at build/run time by every app

**Contract & core**
- `libs/shared/contract`: schemas for the operational objects (Envelope, ErrorEnvelope, HealthStatus, VersionInfo)
- `libs/php/churchos-core`: those objects + `HealthService` port, pure PHP, unit-tested
- `libs/ts/churchos-core`: types generated from the schemas, API client with timeout + error handling

**Apps**
- `apps/api-laravel`: `GET /api/health` via the core; MariaDB connection check
- `apps/admin`: placeholder page showing version + API health (proves admin → API wiring)
- `apps/web`: placeholder, built but **not** deployed to `/` (the old site stays live)

**Testing**
- PHPUnit for PHP, Vitest for TS
- Contract suite: validates real HTTP responses from a running API against the schemas
- End-to-end harness: a browser test opens the real admin, against the real API and a real MariaDB (⚖ D6 tool choice)

**CI/CD**
- CI on PRs: lint · static analysis · unit · contract · e2e, with PHP 8.4 + MariaDB 11.4 service containers to mirror the host
- Deploy workflows: `staging` → test.libbynaz.org, `main` → libbynaz.org (`/api`, `/admin` only)
- Atomic release + migrate + health check + automatic rollback

**Hosting (done with you, documented as a runbook)**
- Switch PHP to 8.4 and confirm extensions (incl. `tokenizer`, `xml`, `xmlwriter`, `zip`)
- Create `test.libbynaz.org`, the two databases (utf8mb4), and a deploy SSH key
- Add the cron entry; set server-side `.env` files (never in git)

**Done when**
- [ ] CI green on a PR, with every job required
- [ ] Merge to `staging` deploys test automatically; `https://test.libbynaz.org/api/health` returns 0.1.0
- [ ] Merge to `main` deploys prod; `https://libbynaz.org/api/health` returns 0.1.0, and the existing site is untouched
- [ ] A failed health check after deploy rolls back automatically (demonstrated once on test)
- [ ] Hosting runbook in `docs/` lets someone repeat the setup

---

## Phase 2 — Design system (theme restoration) → 0.2.0

**Goal:** Restore the original Kootenai theme, make contrast failures impossible to
merge, and give both apps the shared look.

- **Drift analysis first.** Compare the original palette
  (`churchos-v7-archive/packages/config/tailwind.config.ts`: full 50–950 scales, a
  teal-tinted charcoal, stone-100 background) with the archived `tokens.css` (charcoal
  50–600 and stone 300–950 dropped; charcoal-700 and stone-100 shifted). Present
  findings and a proposed palette for approval.
- `libs/ts/theme`: tokens + **semantic** tokens (`surface`, `surface-raised`,
  `text`, `text-muted`, `card-header-bg`, `card-header-text`, …) for light and dark.
  Components use semantic tokens only.
- **Contrast gate in CI:** every approved foreground/background pair is checked
  against WCAG AA (4.5:1 body text, 3:1 large text and UI). Plus accessibility checks
  on rendered pages in the e2e suite.
- `libs/ts/ui`: Vue components (button, card, badge, form controls, scripture
  callout, container, section), each tested
- Fonts: Cinzel / Lora / DM Sans. Self-hosted vs Google Fonts is a privacy and
  performance decision to make at plan review.
- `/design` reference page (noindex); admin shell layout (sidebar, topbar, version badge)

**Done when:** the contrast gate passes in light and dark mode; `/design` and the admin
shell are verified on test and live on prod (`/admin`, `/design` only).

---

## Phase 3 — Core platform → 0.3.0

**Goal:** Everything modules depend on: login, users, roles, site settings, the
module registry, and an audit trail. All of it manageable in the admin.

- Auth: Laravel's first-party cookie-based SPA auth (Sanctum, ⚖ D7). Session in an
  HttpOnly cookie, CSRF-protected; no tokens in JS-readable storage.
- Passwords hashed with PHP's native `password_hash` (Argon2id where available);
  login throttling; password reset and email verification
- Two-factor sign-in (authenticator-app codes) required for staff and above (⚖ D9)
- Roles `superadmin → admin → staff → member → guest`. The authorization rules live in
  the PHP core; Laravel policies only call them. Enforced in the API.
- Admin: sign in/out, password reset (email), user list, invite user, change role,
  disable user
- Site settings (church name, timezone `America/Denver`, contact info, service times,
  social links) — typed, validated, editable in the admin
- Module registry: list modules, enable/disable, edit module settings (schema-driven
  forms); secret settings encrypted at rest and never returned to the browser
- Audit log: who changed what, when; viewable by admins
- Email: Laravel mail over the host's SMTP, for password reset and invites

**Done when:** you can sign in to `libbynaz.org/admin`, invite a staff user, change
site settings, and see each action in the audit log, all verified on test first.
Role checks are covered by e2e tests against the real API.

---

## Phase 4 — Site content & cutover → 1.0.0 "Kootenai"

**Goal:** The new ChurchOS site replaces the current libbynaz.org, with everything on
it editable in the admin and the restored theme applied.

- **Inventory first:** list every page, section and asset on the current site, and
  agree what moves over. (The current site renders client-side, so this is done in a
  browser together.)
- Pages module: pages made of ordered **content blocks** (rich text, hero, image,
  call-to-action, service times, contact, embed, scripture). Draft/publish. SEO title
  and description per page.
- Navigation and footer managed in the admin
- **Temporary sermons:** a Logos embed block configured with the channel ID
  (`13608627`). New functionality; replaced in Phase 6.
- Contact form → email to a configured address (rate-limited)
- 404 page, sitemap, robots.txt, redirects from any old URLs
- Static generation: the public site rebuilds and redeploys when content is published
  (⚖ D8 — how a publish triggers a rebuild on shared hosting)
- Lighthouse check in CI (target ≥ 90 now, ≥ 95 by Phase 12)

**Cutover:** verify everything on test.libbynaz.org → release to prod (`/` switches to
the new site) → keep the old site's files for a quick rollback for one release.

**Done when:** libbynaz.org serves ChurchOS; every page is editable in the admin; the
old site's files are retired after one stable release.

---

## Phase 5 — Prayer board module → 1.1.0 "Cabinet"

**Goal:** Visitors submit prayer requests; nothing becomes public without staff approval.

- Submission form (public), rate-limited per real client IP, with spam protection
  (honeypot field + timing check — native, no third-party service)
- Every submission is stored as **`pending`**. Optional AI pre-screen only *labels*
  submissions for staff (provider pluggable, off by default); it never publishes.
- Admin queue: approve, reject (with private reason), edit for privacy before
  publishing, mark answered, post updates
- Public board (approved only; never email or moderation data) and optional
  members-only view
- Prayer-chain email on approval (configurable list)
- Expiry / archive of old requests (uses Phase 6 scheduler if it exists; otherwise
  on-read filtering)
- Submitter always sees the same confirmation, whatever happens to the request

**Done when:** a request submitted on test appears in the admin queue, is approved,
reaches the public board and the prayer-chain email. Proven by an e2e test against the
real stack, then on prod.

---

## Phase 6 — Scheduled tasks + Sermons module → 1.2.0 "Fisher"

### 6a. Scheduled tasks (system module)

**Goal:** Admins schedule recurring jobs in plain language; modules register the jobs.

- **Heartbeat vs schedule:** the single cPanel cron entry ticks every minute. That is
  only the heartbeat. Each task's own schedule decides whether it runs on a tick.
- Recurrence options (stored as data, defined in DOMAIN-MODEL):
  every N minutes/hours/days/weeks · N times per day/week · specific weekdays at a
  time (e.g. every Monday 18:00, weekdays 16:00) · monthly · advanced cron expression
- Ends: never · after N runs · on a date
- Retry policy: max attempts + back-off. Overlap protection (a task never runs twice at once).
- Times entered in the church's timezone and stored in UTC
- Admin: list tasks, enable/disable, edit schedule with a human-readable preview
  ("Every weekday at 4:00 PM — next run Tue Oct 13, 4:00 PM"), **Run now**, run
  history with status and messages
- Recurrence logic lives in the PHP core (pure, heavily unit-tested); Laravel only
  provides the heartbeat command and storage

### 6b. Sermons module

**Goal:** Sermons from Logos appear on the site with full detail, replacing the
Phase 4 embed. The Sermon model will be revisited at plan review.

- Source adapter (PHP core): Logos RSS feed
  `https://sermons.logos.com/api/channels/13608627/feed` → domain `Sermon`
  (title, description, date, audio, duration, link)
- Enrichment adapter: each sermon's public page provides the cover image, speaker,
  series, passage, and possibly transcript/video. **Undocumented and fragile:** it must
  fail soft and never block the feed import.
- Admin edits (speaker, series, passage, cover) are never overwritten by a sync
- Sync task `sermons.sync` with a default schedule (e.g. Sundays + Mondays); configurable
- Public: sermon list with search and series filter, sermon detail with audio player
  (and video/transcript if available), "Latest sermon" block for pages
- Sermon dates are calendar dates (the feed's midnight-GMT timestamps would otherwise show the previous day in Montana)

**Done when:** the sync runs on schedule on prod, the embed is retired, and admin
overrides survive a re-sync (tested).

---

## Phase 7 — Events module → 1.3.0 "Quartz"

- Events with date/time (timezone-aware), location, description, image, recurring events
  (reusing the Phase 6 recurrence model)
- Admin CRUD; public calendar/list and detail pages; "Upcoming events" block
- iCal feed export (subscribe from phone calendars)

---

## Phases 8–12 — outline

| # | Phase | Notes carried over |
|---|---|---|
| 8 | **Giving** | Stripe.js holds all card input; webhook signature verified; members see only their own history; no bulk export. Settings via module config. |
| 9 | **Member directory** | Member role minimum, never public; consent before listing; per-field visibility; personal data encrypted at rest (column-level); every read audited; no bulk export. |
| 10 | **External login providers** | Microsoft, Google, Apple via Laravel's first-party OAuth package (Socialite — dependency approval); group → role mapping. |
| 11 | **Integrations** | Email providers (MS365 Graph, Gmail), calendar sync (Google/Outlook), AI moderation providers (Gloo, Grok), storage (B2/S3). Each one is a source/sink adapter behind a core port. |
| 12 | **Portability & second backend** | New-church setup guide and installer; Lighthouse ≥ 95; security review; restore FastAPI as `apps/api-fastapi` + `libs/python/churchos-core`, passing the same contract suite. |

---

## Lessons carried over from the archived build

These are the failure modes the new workflow is designed to prevent:

| What happened | Prevented by |
|---|---|
| Admin app never reached the API; unit tests passed because every `$fetch` was mocked | E2E tests against the real stack are a done criterion for every phase |
| Prayer requests auto-published when AI moderation was unavailable | Pending-first design; AI can only label |
| Phases marked ✅ with unchecked done criteria | "Done means live", and the checklist is reviewed at release |
| Docs described intended behaviour, not actual behaviour | Docs change first at plan review, and the e2e tests prove the behaviour |
| Theme drift and unreadable card headers | Semantic tokens + CI contrast gate |
| Migrations applied by hand; a migration silently never applied | Deploy pipeline runs migrations and health-checks every release |
| Version hardcoded in footer/badge, never bumped | Read from `version.json`; bumped as part of the release PR |
| Unmerged fixes and local-only branches | Release checklist includes "no orphan branches" |

---

## Decisions

Proposed defaults. Each needs your ✅ or a change before the phase that uses it.

| # | Decision | Proposed | Needed by |
|---|---|---|---|
| D1 | Repo layout | `apps/` + `libs/<lang>/` as in §2 | Phase 1 |
| D2 | URL layout | One domain per env: `/`, `/admin`, `/api` | Phase 1 |
| D3 | Release cadence | Every two weeks | Phase 1 |
| D4 | Version map | 0.x pre-cutover; **1.0.0 Kootenai = cutover**; one codename per module release | Phase 1 |
| D5 | FastAPI code in the working tree | Remove (kept in archive tag) rather than leave unmaintained | Phase 1 |
| D6 | E2E browser test tool | Playwright (dependency approval) | Phase 1 |
| D7 | Auth | Laravel Sanctum cookie-based SPA auth (first-party) | Phase 3 |
| D8 | Rebuild the static site on publish | Admin publish → API queues a rebuild → GitHub Actions builds and deploys (needs a scoped GitHub token on the server) vs. render public pages at runtime from the API | Phase 4 |
| D9 | Two-factor sign-in | Required for staff and above; optional for members | Phase 3 |
