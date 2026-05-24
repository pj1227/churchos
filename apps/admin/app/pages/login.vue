<!--
  pages/login.vue — Admin login page.

  What it does:
    Provides email/password sign-in for staff, admin, and superadmin users.
    On success, navigates to the dashboard. Errors are shown inline.

  Why it exists at this layer:
    The admin app has no public pages — every route requires auth.
    The middleware redirects unauthenticated users here; this page is the
    only one exempt from the auth guard.

  How it connects:
    - useAuthStore().signIn() handles Supabase auth + profile fetch
    - middleware/auth.ts redirects logged-in users away from this page
    - Design system classes (btn-primary, form-input, etc.) from @churchos/config
-->

<script setup lang="ts">
import { ref } from 'vue'
import { useAuthStore } from '~/stores/auth'

definePageMeta({ layout: false }) // No nav/shell on the login page

const auth = useAuthStore()

const email = ref('')
const password = ref('')
const error = ref<string | null>(null)
const loading = ref(false)

async function handleSignIn() {
  error.value = null
  loading.value = true

  try {
    await auth.signIn(email.value, password.value)
    await navigateTo('/')
  } catch (err: unknown) {
    error.value = err instanceof Error
      ? err.message
      : 'Sign in failed. Check your credentials and try again.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div
    class="min-h-screen flex items-center justify-center bg-stone-50 dark:bg-charcoal-900 px-4"
  >
    <div class="w-full max-w-sm">
      <!-- Wordmark -->
      <div class="text-center mb-8">
        <h1
          style="font-family: var(--font-display)"
          class="text-3xl font-bold text-forest-500 dark:text-forest-400"
        >
          ChurchOS
        </h1>
        <p
          style="font-family: var(--font-ui)"
          class="text-charcoal-900/60 dark:text-stone-300/60 text-sm mt-1"
        >
          Admin Dashboard
        </p>
      </div>

      <!-- Card -->
      <div class="co-card">
        <h2
          style="font-family: var(--font-display)"
          class="text-xl font-semibold text-charcoal-900 dark:text-stone-50 mb-6"
        >
          Sign in
        </h2>

        <form class="space-y-4" @submit.prevent="handleSignIn">
          <!-- Email -->
          <div>
            <label
              for="email"
              style="font-family: var(--font-ui)"
              class="form-label"
            >
              Email
            </label>
            <input
              id="email"
              v-model="email"
              type="email"
              autocomplete="email"
              required
              class="form-input mt-1"
              placeholder="you@libbynaz.org"
            >
          </div>

          <!-- Password -->
          <div>
            <label
              for="password"
              style="font-family: var(--font-ui)"
              class="form-label"
            >
              Password
            </label>
            <input
              id="password"
              v-model="password"
              type="password"
              autocomplete="current-password"
              required
              class="form-input mt-1"
              placeholder="••••••••"
            >
          </div>

          <!-- Error message -->
          <p
            v-if="error"
            style="font-family: var(--font-ui)"
            class="text-red-600 dark:text-red-400 text-sm"
            role="alert"
          >
            {{ error }}
          </p>

          <!-- Submit -->
          <button
            type="submit"
            class="btn-primary w-full"
            :disabled="loading"
          >
            {{ loading ? 'Signing in…' : 'Sign in' }}
          </button>
        </form>
      </div>

      <!-- Version -->
      <p
        style="font-family: var(--font-ui)"
        class="text-center text-xs text-charcoal-900/30 dark:text-stone-300/30 mt-6"
      >
        v0.1.0 · Kootenai
      </p>
    </div>
  </div>
</template>
