# Changelog

All notable changes to ChurchOS will be documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
Versioning follows [Semantic Versioning](https://semver.org/).

---

## [Unreleased] — Phase 2: Public Website

### Added
- Public site layout (`apps/web/app/layouts/default.vue`) — AppNav + slot + AppFooter with dark-mode class root
- `AppNav` component — sticky forest-colored nav with church name, Home/Sermons/About/Contact links, Give CTA, mobile hamburger drawer
- `AppFooter` component — church address, quick links, service times, version string, copyright
- Homepage (`/`) — hero with CTA, scripture callout, latest sermon featured card, upcoming events strip, connect CTA
- Sermons listing page (`/sermons`) — grid of 6 placeholder sermon cards with title, speaker, scripture, series badge, date
- About page (`/about`) — mission statement, Micah 6:8 scripture callout, service times, beliefs summary
- Contact page (`/contact`) — form (name, email, message textarea, submit button) + church address sidebar
- Vitest page + component tests (28 tests, TDD — tests written before implementation)
- Nuxt auto-import stubs (`tests/setup.ts`) so pages run cleanly under vitest without a Nuxt instance
- Static generation enabled via `nitro: { preset: 'static' }` in `nuxt.config.ts`

---

## [0.2.0] — Phase 1: Design System — 2026-05-23

### Added
- Tailwind CSS v4 design tokens (`packages/config/src/tokens.css`) — forest, kootenai, gold, charcoal, stone palettes + Cinzel/Lora/DM Sans font stacks
- Shared Vue component library (`packages/ui`): CoButton, CoCard, CoCardFeatured, CoBadge, CoFormInput, CoScriptureCallout, CoContainer, CoSection
- Vitest component tests for all UI components (TDD — tests written before implementation)
- Dark mode wired into both Nuxt apps via `@nuxtjs/color-mode` class strategy
- Design system demo page at `/design` in apps/web

---

## [0.1.0] — Phase 0: Repo & Tooling — 2026-05-23

### Added
- pnpm workspaces + Turborepo v2 monorepo scaffold
- `apps/web` — Nuxt 4 public site stub (compatibilityVersion: 4)
- `apps/admin` — Nuxt 4 admin dashboard stub (port 3001, noindex)
- `apps/api` — FastAPI (Python 3.12) with `/health` endpoint
- `packages/ui` — shared Vue component library stub
- `packages/types` — shared TypeScript definitions (Role, VersionInfo)
- `packages/config` — Tailwind design token stub (forest, kootenai, gold, charcoal, stone palettes; Cinzel/Lora/DM Sans fonts)
- `version.json` — single source of truth for version (`0.1.0`) and codename (`Kootenai`)
- GitHub Actions: `ci.yml` (lint + type-check + build + pytest on PRs), `deploy-staging.yml`, `deploy-production.yml`
- Branch protection on `main` and `staging` (PR required, CI must pass, no direct pushes)
- 4 passing pytest TDD tests for `/health` endpoint (status, version, codename)
- `.gitignore` covering Node, Python, Nuxt, editors, .env files

### Repository
- GitHub: https://github.com/pj1227/churchos (public)
- Branches: `main`, `staging`, `dev`, `feature/phase-0-repo-setup`
