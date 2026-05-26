/**
 * middleware/auth.ts — Route guard for the admin dashboard.
 *
 * What it does:
 *   Runs before every navigation in apps/admin. Redirects unauthenticated
 *   users to /login and redirects already-logged-in users away from /login.
 *
 * Why it exists at this layer:
 *   Nuxt global middleware (files in app/middleware/ without `.server` or
 *   `.client` suffix) runs on both server and client, making it SSR-safe.
 *   Every admin route is protected by default — staff only.
 *
 * How it connects:
 *   - useSupabaseUser() is provided by @nuxtjs/supabase (auto-imported)
 *   - The Supabase session is rehydrated from the HttpOnly cookie on SSR,
 *     so useSupabaseUser() is populated before this middleware runs
 *   - navigateTo() is a Nuxt auto-import
 *
 * Security note:
 *   This middleware prevents navigation to protected pages but is NOT a
 *   substitute for server-side auth. Every API call from the admin app
 *   includes the Bearer token, which FastAPI verifies independently.
 *   Client-side guards are UX; server-side JWT verification is security.
 */
export default defineNuxtRouteMiddleware((to) => {
  const user = useSupabaseUser()

  // Already on login page — redirect authenticated users to dashboard
  if (to.path === '/login') {
    if (user.value) {
      return navigateTo('/')
    }
    return // Let unauthenticated users reach the login page
  }

  // All other routes require authentication
  if (!user.value) {
    return navigateTo('/login')
  }
})
