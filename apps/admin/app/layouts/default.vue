<!--
  layouts/default.vue — Admin dashboard shell.

  What it does:
    Wraps every admin page (except login, which uses layout: false) with a
    persistent sidebar and topbar. The sidebar contains brand, navigation,
    and version badge. The topbar shows the current user and sign-out.

  Why it exists at this layer:
    Nuxt 4 layouts in app/layouts/ are automatically available via
    definePageMeta({ layout: 'default' }) or as the default for any page
    that doesn't specify otherwise.

  How it connects:
    - app/stores/auth.ts: profile, isAuthenticated, signOut
    - app/middleware/auth.ts: redirects unauthenticated users before layout renders
    - app/pages/sermons/index.vue, events/index.vue: rendered in the <slot />
-->

<script setup lang="ts">
import { computed } from 'vue'
import { useAuthStore } from '~/stores/auth'

const auth  = useAuthStore()
const label = computed(() =>
  auth.profile?.display_name || auth.profile?.email || 'User'
)

async function handleSignOut() {
  await auth.signOut()
  await navigateTo('/login')
}

const VERSION  = '0.1.0'
const CODENAME = 'Kootenai'

const navItems = [
  { label: 'Sermons',  to: '/sermons',  icon: '🎙' },
  { label: 'Events',   to: '/events',   icon: '📅' },
  { label: 'Prayer',   to: '/prayer',   icon: '🙏' },
  { label: 'Settings', to: '/settings', icon: '⚙️' },
]
</script>

<template>
  <div class="min-h-screen flex bg-stone-50 dark:bg-charcoal-900">

    <!-- ── Sidebar ─────────────────────────────────────────────────────── -->
    <aside
      class="w-56 flex-shrink-0 flex flex-col bg-white dark:bg-charcoal-900
             border-r border-stone-200 dark:border-stone-800"
    >
      <!-- Brand -->
      <div class="px-5 py-6 border-b border-stone-200 dark:border-stone-800">
        <span
          style="font-family: var(--font-display)"
          class="text-xl font-bold text-forest-500 dark:text-forest-400"
        >
          ChurchOS
        </span>
        <p
          style="font-family: var(--font-ui)"
          class="text-xs text-charcoal-900/40 dark:text-stone-400 mt-0.5"
        >
          Admin
        </p>
      </div>

      <!-- Nav -->
      <nav class="flex-1 px-3 py-4 space-y-1">
        <NuxtLink
          v-for="item in navItems"
          :key="item.to"
          :to="item.to"
          style="font-family: var(--font-ui)"
          class="flex items-center gap-3 px-3 py-2 rounded-lg text-sm
                 text-charcoal-900/70 dark:text-stone-300
                 hover:bg-stone-100 dark:hover:bg-stone-800
                 transition-colors"
          active-class="bg-forest-500/10 text-forest-600 dark:text-forest-400 font-medium"
        >
          <span>{{ item.icon }}</span>
          <span>{{ item.label }}</span>
        </NuxtLink>
      </nav>

      <!-- Version badge -->
      <div class="px-5 py-4 border-t border-stone-200 dark:border-stone-800">
        <span
          style="font-family: var(--font-ui)"
          class="text-xs text-charcoal-900/30 dark:text-stone-500"
        >
          v{{ VERSION }} · {{ CODENAME }}
        </span>
      </div>
    </aside>

    <!-- ── Main area ───────────────────────────────────────────────────── -->
    <div class="flex-1 flex flex-col min-w-0">

      <!-- Topbar -->
      <header
        class="h-14 flex items-center justify-between px-6
               bg-white dark:bg-charcoal-900
               border-b border-stone-200 dark:border-stone-800"
      >
        <!-- Page title slot — pages can override via provide/inject later -->
        <div />

        <!-- User + sign-out -->
        <div class="flex items-center gap-4">
          <span
            style="font-family: var(--font-ui)"
            class="text-sm text-charcoal-900/70 dark:text-stone-300"
          >
            {{ label }}
          </span>
          <button
            data-testid="sign-out-btn"
            style="font-family: var(--font-ui)"
            class="btn-ghost text-sm px-3 py-1"
            @click="handleSignOut"
          >
            Sign out
          </button>
        </div>
      </header>

      <!-- Page content -->
      <main class="flex-1 p-6 overflow-auto">
        <slot />
      </main>
    </div>

  </div>
</template>
