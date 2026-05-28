<!--
  pages/events/index.vue — Events index page.

  What it does:
    Lists all church events fetched from the API. Each row shows the title,
    location, start date, and a Published/Draft status badge. Each row links
    to the edit page at /events/:id/edit.

  Why it exists at this layer:
    Nuxt 4 file-based routing maps app/pages/events/index.vue to the
    /events route, which the sidebar nav links to.

  How it connects:
    - layouts/default.vue wraps this page (sidebar + topbar)
    - middleware/auth.ts guards the route (requires authenticated user)
    - $fetch calls the FastAPI GET /events endpoint
-->

<script setup lang="ts">
import { ref, onMounted } from 'vue'

interface ChurchEvent {
  id:           string
  title:        string
  location:     string | null
  start_at:     string
  end_at:       string | null
  is_published: boolean
  category:     string | null
  recurrence:   string
}

const events   = ref<ChurchEvent[]>([])
const loading  = ref(true)
const fetchErr = ref<string | null>(null)

function formatDate(iso: string): string {
  try {
    return new Date(iso).toLocaleDateString('en-US', {
      year:  'numeric',
      month: 'short',
      day:   'numeric',
    })
  } catch {
    return iso
  }
}

onMounted(async () => {
  try {
    const data = await $fetch<ChurchEvent[]>('/events')
    events.value = data
  } catch (err: unknown) {
    fetchErr.value = err instanceof Error ? err.message : 'Failed to load events.'
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div>
    <!-- Heading row -->
    <div class="mb-6 flex items-center justify-between">
      <h1
        style="font-family: var(--font-display)"
        class="text-2xl font-semibold text-charcoal-900 dark:text-stone-50"
      >
        Events
      </h1>
      <NuxtLink
        to="/events/new"
        style="font-family: var(--font-ui)"
        class="btn-primary text-sm px-4 py-2"
      >
        + Add Event
      </NuxtLink>
    </div>

    <!-- Loading -->
    <div
      v-if="loading"
      style="font-family: var(--font-ui)"
      class="text-charcoal-900/50 dark:text-stone-400 text-sm"
    >
      Loading…
    </div>

    <!-- Error -->
    <div
      v-else-if="fetchErr"
      style="font-family: var(--font-ui)"
      class="text-red-600 text-sm"
    >
      {{ fetchErr }}
    </div>

    <!-- Empty state -->
    <div
      v-else-if="events.length === 0"
      style="font-family: var(--font-ui)"
      class="text-charcoal-900/50 dark:text-stone-400 text-sm py-12 text-center"
    >
      No events found. Add one to get started.
    </div>

    <!-- Event list -->
    <div
      v-else
      class="co-card overflow-hidden p-0"
    >
      <table class="w-full text-sm">
        <thead>
          <tr class="border-b border-stone-200 dark:border-stone-800">
            <th
              style="font-family: var(--font-ui)"
              class="px-4 py-3 text-left font-medium text-charcoal-900/60 dark:text-stone-400"
            >
              Title
            </th>
            <th
              style="font-family: var(--font-ui)"
              class="px-4 py-3 text-left font-medium text-charcoal-900/60 dark:text-stone-400"
            >
              Date
            </th>
            <th
              style="font-family: var(--font-ui)"
              class="px-4 py-3 text-left font-medium text-charcoal-900/60 dark:text-stone-400"
            >
              Location
            </th>
            <th
              style="font-family: var(--font-ui)"
              class="px-4 py-3 text-left font-medium text-charcoal-900/60 dark:text-stone-400"
            >
              Status
            </th>
            <th class="px-4 py-3" />
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="event in events"
            :key="event.id"
            class="border-b border-stone-100 dark:border-stone-800 last:border-0
                   hover:bg-stone-50 dark:hover:bg-stone-800/40 transition-colors"
          >
            <!-- Title -->
            <td
              style="font-family: var(--font-ui)"
              class="px-4 py-3 font-medium text-charcoal-900 dark:text-stone-100"
            >
              {{ event.title }}
            </td>

            <!-- Date -->
            <td
              style="font-family: var(--font-ui)"
              class="px-4 py-3 text-charcoal-900/60 dark:text-stone-400 tabular-nums"
            >
              {{ formatDate(event.start_at) }}
            </td>

            <!-- Location -->
            <td
              style="font-family: var(--font-ui)"
              class="px-4 py-3 text-charcoal-900/70 dark:text-stone-300"
            >
              {{ event.location ?? '—' }}
            </td>

            <!-- Status badge -->
            <td class="px-4 py-3">
              <span
                v-if="event.is_published"
                style="font-family: var(--font-ui)"
                class="badge-forest text-xs"
              >
                Published
              </span>
              <span
                v-else
                style="font-family: var(--font-ui)"
                class="badge-kootenai text-xs"
              >
                Draft
              </span>
            </td>

            <!-- Edit link -->
            <td class="px-4 py-3 text-right">
              <NuxtLink
                :to="`/events/${event.id}/edit`"
                style="font-family: var(--font-ui)"
                class="text-forest-500 dark:text-forest-400 hover:underline text-sm"
              >
                Edit
              </NuxtLink>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
