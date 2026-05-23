# Changelog

All notable changes to ChurchOS will be documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
Versioning follows [Semantic Versioning](https://semver.org/).

---

## [Unreleased] — Phase 1: Design System

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
