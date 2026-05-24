/**
 * tests/setup.ts — Vitest global setup for apps/admin
 *
 * What it does:
 *   Stubs Nuxt auto-imported composables so stores and components can be
 *   tested without a running Nuxt instance.
 *
 * Why it exists at this layer:
 *   Nuxt injects composables like useSupabaseClient, useSupabaseUser,
 *   navigateTo, and $fetch at build time via its Vite plugin. Vitest
 *   skips that plugin, so the symbols would be undefined at runtime.
 *   vi.stubGlobal places them on globalThis before any test executes.
 *
 * How it connects:
 *   Referenced by vitest.config.ts setupFiles. Does NOT affect the
 *   running Nuxt app — only active during vitest runs.
 */
import { vi } from 'vitest'

// ── Nuxt head / SEO composables ──────────────────────────────────────────
vi.stubGlobal('useSeoMeta', vi.fn())
vi.stubGlobal('useHead', vi.fn())
vi.stubGlobal('definePageMeta', vi.fn())

// ── Color mode ───────────────────────────────────────────────────────────
vi.stubGlobal('useColorMode', () => ({
  value: 'light',
  preference: 'system',
}))

// ── Nuxt router ──────────────────────────────────────────────────────────
vi.stubGlobal('navigateTo', vi.fn())
vi.stubGlobal('useRoute', () => ({ path: '/', params: {}, query: {} }))
vi.stubGlobal('useRouter', () => ({ push: vi.fn(), replace: vi.fn() }))

// ── Supabase composables (@nuxtjs/supabase auto-imports) ─────────────────
// Tests that need specific Supabase behaviour override these per-test
// with vi.mocked(...).mockReturnValue(...).
vi.stubGlobal('useSupabaseClient', () => ({
  auth: {
    signInWithPassword: vi.fn().mockResolvedValue({ error: null }),
    signOut: vi.fn().mockResolvedValue({}),
    getSession: vi.fn().mockResolvedValue({ data: { session: null } }),
  },
}))

vi.stubGlobal('useSupabaseUser', () => ({ value: null }))

// ── $fetch (Nuxt's isomorphic fetch, used in fetchMe) ────────────────────
vi.stubGlobal('$fetch', vi.fn())
