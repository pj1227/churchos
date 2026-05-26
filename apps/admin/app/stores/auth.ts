/**
 * stores/auth.ts — Pinia auth store for the admin dashboard.
 *
 * What it does:
 *   Holds the authenticated user's profile in reactive memory and exposes
 *   actions for sign-in, sign-out, and profile refresh. This is the single
 *   source of truth for "who is logged in" across the admin app.
 *
 * Why it exists at this layer:
 *   Keeping auth state in Pinia (not in a component or composable) means
 *   any page, layout, or component can read `isAuthenticated` and `profile`
 *   without prop drilling or provide/inject.
 *
 * Security contract (enforced by tests):
 *   - `profile` lives in reactive memory — never written to localStorage
 *   - The Supabase access token is managed by @nuxtjs/supabase internally;
 *     we never store it ourselves
 *   - The refresh token is in an HttpOnly cookie managed by Supabase SSR
 *
 * How it connects:
 *   - app/middleware/auth.ts reads `isAuthenticated` to gate every route
 *   - app/pages/login.vue calls `signIn` on form submit
 *   - @nuxtjs/supabase provides useSupabaseClient (auto-imported by Nuxt)
 *   - Our FastAPI /me endpoint is called by fetchMe to get the app profile
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export interface Profile {
  id: string
  email: string
  display_name: string | null
  role: 'superadmin' | 'admin' | 'staff' | 'member' | 'guest'
  church_slug: string
}

export const useAuthStore = defineStore('auth', () => {
  // ── State ──────────────────────────────────────────────────────────────
  // profile is the only piece of state. It lives in memory; never touches
  // localStorage, sessionStorage, or any other persistent browser storage.
  const profile = ref<Profile | null>(null)

  // ── Derived ───────────────────────────────────────────────────────────
  const isAuthenticated = computed(() => profile.value !== null)

  const role = computed(() => profile.value?.role ?? 'guest')

  // ── Mutations ─────────────────────────────────────────────────────────
  function setProfile(p: Profile): void {
    profile.value = p
  }

  function clearProfile(): void {
    profile.value = null
  }

  // ── Actions ───────────────────────────────────────────────────────────

  /**
   * Sign in with email + password via Supabase Auth.
   * On success, fetches the app profile from our FastAPI /me endpoint.
   * Throws if Supabase returns an error (wrong credentials, unconfirmed, etc.)
   */
  async function signIn(email: string, password: string): Promise<void> {
    const client = useSupabaseClient()
    const { error } = await client.auth.signInWithPassword({ email, password })
    if (error) throw error
    await fetchMe()
  }

  /**
   * Sign out via Supabase Auth and clear local profile state.
   * The HttpOnly refresh token cookie is invalidated server-side by Supabase.
   */
  async function signOut(): Promise<void> {
    const client = useSupabaseClient()
    await client.auth.signOut()
    clearProfile()
  }

  /**
   * Fetch the authenticated user's app profile from our FastAPI /me endpoint.
   *
   * Called after signIn and on app init (in app.vue) to rehydrate profile
   * state from a valid session. If there is no active session, clears profile.
   *
   * Why call our API instead of Supabase directly:
   *   Our FastAPI /me endpoint returns the `public.profiles` row, which
   *   includes the RBAC role and church_slug — fields Supabase Auth doesn't
   *   know about. The Supabase session gives us identity; our DB gives us
   *   the app-level role.
   */
  async function fetchMe(): Promise<void> {
    const client = useSupabaseClient()
    const { data: { session } } = await client.auth.getSession()

    if (!session) {
      clearProfile()
      return
    }

    try {
      const data = await $fetch<Profile>('/api/me', {
        headers: { Authorization: `Bearer ${session.access_token}` },
      })
      setProfile(data)
    } catch {
      // Token valid but no profile row — clear state, force re-login
      clearProfile()
    }
  }

  return {
    // State
    profile,
    // Derived
    isAuthenticated,
    role,
    // Mutations (used directly in tests and by actions)
    setProfile,
    clearProfile,
    // Actions
    signIn,
    signOut,
    fetchMe,
  }
})
