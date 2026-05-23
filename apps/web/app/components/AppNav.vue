<!--
  app/components/AppNav.vue — Public site navigation bar

  What it does:
    Renders the sticky top navigation with the church name/logo on the left,
    nav links in the centre, and a "Give" CTA button on the right. Includes
    a mobile hamburger toggle that shows/hides the link list.

  Why it exists at this layer:
    Navigation is shared across every public page via the default layout.
    Keeping it as a standalone component makes it independently testable and
    replaceable.

  How it connects:
    - Consumed by app/layouts/default.vue
    - Uses NuxtLink (Nuxt auto-imported) for client-side routing
    - Reads useColorMode() to apply dark/light toggle
    - Styled entirely with design-system tokens from @churchos/config
-->

<script setup lang="ts">
import { ref, computed } from 'vue'

const colorMode = useColorMode()
const mobileOpen = ref(false)

const isDark = computed(() => colorMode.value === 'dark')

function toggleDark() {
  colorMode.preference = isDark.value ? 'light' : 'dark'
}

const navLinks = [
  { label: 'Home',     to: '/' },
  { label: 'Sermons',  to: '/sermons' },
  { label: 'About',    to: '/about' },
  { label: 'Contact',  to: '/contact' },
]
</script>

<template>
  <nav class="sticky top-0 z-30 bg-forest-500 dark:bg-charcoal-900 shadow-md">
    <div class="co-container flex items-center justify-between h-16">

      <!-- Brand -->
      <NuxtLink
        to="/"
        class="flex items-center gap-2 no-underline"
        aria-label="Libby Church — home"
      >
        <span
          style="font-family: var(--font-display)"
          class="text-white text-lg font-semibold tracking-wide leading-tight"
        >
          Libby Church<span class="hidden sm:inline"> of the Nazarene</span>
        </span>
      </NuxtLink>

      <!-- Desktop nav links -->
      <ul class="hidden md:flex items-center gap-6 list-none m-0 p-0">
        <li v-for="link in navLinks" :key="link.to">
          <NuxtLink
            :to="link.to"
            class="text-white/80 hover:text-white font-medium transition-colors"
            style="font-family: var(--font-ui)"
            active-class="text-white underline underline-offset-4"
          >
            {{ link.label }}
          </NuxtLink>
        </li>
      </ul>

      <!-- Desktop actions -->
      <div class="hidden md:flex items-center gap-3">
        <!-- Dark mode toggle -->
        <button
          class="text-white/70 hover:text-white transition-colors p-2 rounded"
          :aria-label="isDark ? 'Switch to light mode' : 'Switch to dark mode'"
          @click="toggleDark"
        >
          {{ isDark ? '☀' : '☾' }}
        </button>

        <!-- Give CTA -->
        <NuxtLink
          to="/give"
          class="btn-secondary !py-1.5 !px-4 text-sm"
          style="font-family: var(--font-ui)"
        >
          Give
        </NuxtLink>
      </div>

      <!-- Mobile hamburger -->
      <button
        class="md:hidden text-white p-2 rounded hover:bg-forest-600 dark:hover:bg-charcoal-700 transition-colors"
        :aria-label="mobileOpen ? 'Close menu' : 'Open menu'"
        @click="mobileOpen = !mobileOpen"
      >
        <span v-if="!mobileOpen">☰</span>
        <span v-else>✕</span>
      </button>

    </div>

    <!-- Mobile drawer -->
    <div v-show="mobileOpen" class="md:hidden bg-forest-600 dark:bg-charcoal-800 border-t border-forest-700 dark:border-charcoal-700">
      <ul class="list-none m-0 p-0 py-2">
        <li v-for="link in navLinks" :key="link.to">
          <NuxtLink
            :to="link.to"
            class="block px-6 py-3 text-white/80 hover:text-white hover:bg-forest-700 dark:hover:bg-charcoal-700 transition-colors"
            style="font-family: var(--font-ui)"
            active-class="text-white bg-forest-700 dark:bg-charcoal-700"
            @click="mobileOpen = false"
          >
            {{ link.label }}
          </NuxtLink>
        </li>
        <li class="px-6 py-3">
          <NuxtLink
            to="/give"
            class="btn-secondary !py-1.5 !px-4 text-sm inline-block"
            style="font-family: var(--font-ui)"
            @click="mobileOpen = false"
          >
            Give
          </NuxtLink>
        </li>
      </ul>
    </div>

  </nav>
</template>
