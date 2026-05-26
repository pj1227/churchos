/**
 * tests/setup.ts — Vitest global setup for apps/web
 *
 * What it does:
 *   Stubs Nuxt auto-imported composables and globals so Vue SFCs can be
 *   mounted with @vue/test-utils without a running Nuxt instance.
 *
 * Why it exists at this layer:
 *   Nuxt auto-imports (useSeoMeta, useHead, definePageMeta, useColorMode,
 *   etc.) are injected by Nuxt's Vite plugin at build time. Vitest runs
 *   without that plugin, so the symbols would be undefined at runtime.
 *   vi.stubGlobal places them on globalThis before any test file executes.
 *
 * How it connects:
 *   Referenced by vitest.config.ts setupFiles. Does NOT affect the running
 *   Nuxt app — only active during vitest runs.
 */
import { vi } from 'vitest'

// Nuxt head / SEO composables — pages call these in <script setup>
vi.stubGlobal('useSeoMeta', vi.fn())
vi.stubGlobal('useHead', vi.fn())
vi.stubGlobal('definePageMeta', vi.fn())

// Color mode — layout and pages read .value for dark/light class.
// preference is a plain string here because tests only write to it (toggleDark),
// never read it as a reactive ref. Avoids importing vue into this setup file
// since apps/web doesn't list vue as a direct dependency.
vi.stubGlobal('useColorMode', () => ({
  value: 'light',
  preference: 'system',
}))

// Router helpers
vi.stubGlobal('useRoute', () => ({ params: {}, query: {}, path: '/' }))
vi.stubGlobal('useRouter', () => ({ push: vi.fn(), replace: vi.fn() }))
vi.stubGlobal('navigateTo', vi.fn())
