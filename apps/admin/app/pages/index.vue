<!--
  pages/index.vue — Admin dashboard home page.

  What it does:
    Landing page after login. Shows a welcome message and quick-nav cards
    to the main content areas (Sermons, Events).

  How it connects:
    - layouts/default.vue wraps this page with sidebar + topbar
    - middleware/auth.ts ensures only authenticated users reach this page
-->

<script setup lang="ts">
import { computed } from 'vue'
import { useAuthStore } from '~/stores/auth'

const auth  = useAuthStore()
const name  = computed(() => auth.profile?.display_name || auth.profile?.email || 'there')

const sections = [
  {
    label:       'Sermons',
    to:          '/sermons',
    description: 'Manage sermon library, edit descriptions, toggle visibility.',
    icon:        '🎙',
    color:       'forest',
  },
  {
    label:       'Events',
    to:          '/events',
    description: 'Create and manage church events, registrations, and recurrence.',
    icon:        '📅',
    color:       'kootenai',
  },
]
</script>

<template>
  <div>
    <!-- Heading -->
    <div class="mb-8">
      <h1
        style="font-family: var(--font-display)"
        class="text-2xl font-semibold text-charcoal-900 dark:text-stone-50"
      >
        Welcome back, {{ name }}
      </h1>
      <p
        style="font-family: var(--font-ui)"
        class="text-charcoal-900/50 dark:text-stone-400 mt-1 text-sm"
      >
        What would you like to manage today?
      </p>
    </div>

    <!-- Quick-nav cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 max-w-2xl">
      <NuxtLink
        v-for="section in sections"
        :key="section.to"
        :to="section.to"
        class="co-card hover:shadow-md transition-shadow group"
      >
        <div class="flex items-start gap-4">
          <span class="text-3xl">{{ section.icon }}</span>
          <div>
            <h2
              style="font-family: var(--font-display)"
              class="text-base font-semibold text-charcoal-900 dark:text-stone-50
                     group-hover:text-forest-500 dark:group-hover:text-forest-400 transition-colors"
            >
              {{ section.label }}
            </h2>
            <p
              style="font-family: var(--font-ui)"
              class="text-sm text-charcoal-900/55 dark:text-stone-400 mt-1"
            >
              {{ section.description }}
            </p>
          </div>
        </div>
      </NuxtLink>
    </div>
  </div>
</template>
