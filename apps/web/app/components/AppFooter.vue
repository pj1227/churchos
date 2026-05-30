<!--
  app/components/AppFooter.vue — Public site footer

  What it does:
    Renders the bottom-of-page footer with the church name and address, quick
    nav links, service times, version string, and copyright notice.

  Why it exists at this layer:
    The project spec requires the version to be visible in the site footer.
    Keeping it as a standalone component makes that requirement testable
    and makes future content updates easy to find.

  How it connects:
    - Consumed by app/layouts/default.vue
    - Version hardcoded to match version.json (will come from useRuntimeConfig
      once the build pipeline injects it in a later phase)
    - Uses NuxtLink for SPA-friendly navigation
-->

<script setup lang="ts">
const version = '0.1.0'
const year = new Date().getFullYear()

const links = [
  { label: 'Home',         to: '/' },
  { label: 'Sermons',      to: '/sermons' },
  { label: 'Prayer Board', to: '/prayer/board' },
  { label: 'Submit Prayer', to: '/prayer' },
  { label: 'About',        to: '/about' },
  { label: 'Contact',      to: '/contact' },
  { label: 'Give',         to: '/give' },
]
</script>

<template>
  <footer class="bg-charcoal-900 dark:bg-black text-stone-200 mt-auto">

    <!-- Main grid -->
    <div class="co-container py-12 grid grid-cols-1 md:grid-cols-3 gap-8">

      <!-- Church identity -->
      <div>
        <p
          style="font-family: var(--font-display)"
          class="text-white text-lg font-semibold mb-2"
        >
          Libby Church of the Nazarene
        </p>
        <address
          style="font-family: var(--font-ui)"
          class="not-italic text-stone-400 text-sm leading-relaxed"
        >
          409 Louisiana Ave<br>
          Libby, MT 59923
        </address>
        <p style="font-family: var(--font-ui)" class="text-stone-400 text-sm mt-2">
          <a href="tel:+14062932931" class="hover:text-white transition-colors">
            (406) 293-2931
          </a>
        </p>
      </div>

      <!-- Quick links -->
      <div>
        <p
          style="font-family: var(--font-ui)"
          class="text-white font-semibold mb-3 text-sm uppercase tracking-wider"
        >
          Quick Links
        </p>
        <ul class="list-none m-0 p-0 space-y-2">
          <li v-for="link in links" :key="link.to">
            <NuxtLink
              :to="link.to"
              style="font-family: var(--font-ui)"
              class="text-stone-400 hover:text-white text-sm transition-colors"
            >
              {{ link.label }}
            </NuxtLink>
          </li>
        </ul>
      </div>

      <!-- Service times -->
      <div>
        <p
          style="font-family: var(--font-ui)"
          class="text-white font-semibold mb-3 text-sm uppercase tracking-wider"
        >
          Service Times
        </p>
        <ul style="font-family: var(--font-ui)" class="list-none m-0 p-0 text-stone-400 text-sm space-y-1">
          <li>Sunday School — 9:30 AM</li>
          <li>Morning Worship — 10:45 AM</li>
          <li>Wednesday Prayer — 6:30 PM</li>
        </ul>
      </div>

    </div>

    <!-- Bottom bar -->
    <div class="border-t border-charcoal-700 dark:border-charcoal-800">
      <div class="co-container py-4 flex flex-col sm:flex-row items-center justify-between gap-2">
        <p style="font-family: var(--font-ui)" class="text-stone-500 text-xs">
          © {{ year }} Libby Church of the Nazarene. All rights reserved.
        </p>
        <p style="font-family: var(--font-ui)" class="text-stone-600 text-xs">
          ChurchOS v{{ version }} "Kootenai"
        </p>
      </div>
    </div>

  </footer>
</template>
