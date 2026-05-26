/**
 * tests/stores/auth.test.ts — TDD anchor for the Pinia auth store.
 *
 * Written BEFORE the store exists. Tests will fail with a module-not-found
 * error until app/stores/auth.ts is created.
 *
 * What we are testing:
 *   useAuthStore — holds the authenticated user's profile in memory.
 *
 * Security contract enforced here:
 *   - profile lives in Pinia reactive state (memory) — never localStorage
 *   - isAuthenticated is derived from profile, not from a stored flag
 *   - setProfile / clearProfile are the only mutation surfaces
 *
 * What we are NOT testing here:
 *   - signIn / signOut (call useSupabaseClient — covered by e2e)
 *   - fetchMe (calls $fetch to our API — covered by e2e)
 *   These are thin wrappers around Supabase and our own /me endpoint;
 *   mocking them here would only test the mock.
 *
 * How it connects:
 *   - app/stores/auth.ts: the store under test
 *   - tests/setup.ts: stubs useSupabaseClient and $fetch so import succeeds
 *   - vitest.config.ts: ~ alias resolves to ./app so imports match Nuxt
 */
import { setActivePinia, createPinia } from 'pinia'
import { useAuthStore } from '~/stores/auth'

const MOCK_PROFILE = {
  id: '550e8400-e29b-41d4-a716-446655440000',
  email: 'joel@libbynaz.org',
  display_name: 'Joel',
  role: 'admin' as const,
  church_slug: 'libby-naz',
}

describe('useAuthStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  // ── Initial state ────────────────────────────────────────────────────

  it('profile is null by default', () => {
    const store = useAuthStore()
    expect(store.profile).toBeNull()
  })

  it('isAuthenticated is false when profile is null', () => {
    const store = useAuthStore()
    expect(store.isAuthenticated).toBe(false)
  })

  // ── setProfile ───────────────────────────────────────────────────────

  it('setProfile stores the profile', () => {
    const store = useAuthStore()
    store.setProfile(MOCK_PROFILE)
    expect(store.profile).toEqual(MOCK_PROFILE)
  })

  it('isAuthenticated is true after setProfile', () => {
    const store = useAuthStore()
    store.setProfile(MOCK_PROFILE)
    expect(store.isAuthenticated).toBe(true)
  })

  // ── clearProfile ─────────────────────────────────────────────────────

  it('clearProfile resets profile to null', () => {
    const store = useAuthStore()
    store.setProfile(MOCK_PROFILE)
    store.clearProfile()
    expect(store.profile).toBeNull()
  })

  it('isAuthenticated is false after clearProfile', () => {
    const store = useAuthStore()
    store.setProfile(MOCK_PROFILE)
    store.clearProfile()
    expect(store.isAuthenticated).toBe(false)
  })

  // ── Security: no localStorage ────────────────────────────────────────

  it('setProfile does not write to localStorage', () => {
    const store = useAuthStore()
    const spy = vi.spyOn(Storage.prototype, 'setItem')
    store.setProfile(MOCK_PROFILE)
    expect(spy).not.toHaveBeenCalled()
    spy.mockRestore()
  })

  it('clearProfile does not write to localStorage', () => {
    const store = useAuthStore()
    store.setProfile(MOCK_PROFILE)
    const spy = vi.spyOn(Storage.prototype, 'setItem')
    store.clearProfile()
    expect(spy).not.toHaveBeenCalled()
    spy.mockRestore()
  })
})
