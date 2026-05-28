<!--
  pages/sermons/index.vue — Sermons index page.

  What it does:
    Lists all sermons fetched from the API. Each row shows the title,
    speaker, date, and a Published/Draft status badge. Each row links
    to the edit page at /sermons/:id/edit.

  Why it exists at this layer:
    Nuxt 4 file-based routing maps app/pages/sermons/index.vue to the
    /sermons route, which the sidebar nav links to.

  How it connects:
    - layouts/default.vue wraps this page (sidebar + topbar)
    - middleware/auth.ts guards the route (requires authenticated user)
    - $fetch calls the FastAPI GET /sermons endpoint
-->

<script setup lang="ts">
import { ref, onMounted } from 'vue'

interface Sermon {
  id:               string
  title:            string
  speaker_name:     string
  series:           string | null
  date:             string
  is_published:     boolean
  duration_seconds: number | null
  thumbnail_url:    string | null
}

const sermons  = ref<Sermon[]>([])
const loading  = ref(true)
const fetchErr = ref<string | null>(null)

onMounted(async () => {
  try {
    const data = await $fetch<Sermon[]>('/sermons')
    sermons.value = data
  } catch (err: unknown) {
    fetchErr.value = err instanceof Error ? err.message : 'Failed to load sermons.'
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
        Sermons
      </h1>
      <NuxtLink
        to="/sermons/new"
        style="font-family: var(--font-ui)"
        class="btn-primary text-sm px-4 py-2"
      >
        + Add Sermon
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
      v-else-if="sermons.length === 0"
      style="font-family: var(--font-ui)"
      class="text-charcoal-900/50 dark:text-stone-400 text-sm py-12 text-center"
    >
      No sermons found. Add one to get started.
    </div>

    <!-- Sermon list -->
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
              Speaker
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
              Status
            </th>
            <th class="px-4 py-3" />
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="sermon in sermons"
            :key="sermon.id"
            class="border-b border-stone-100 dark:border-stone-800 last:border-0
                   hover:bg-stone-50 dark:hover:bg-stone-800/40 transition-colors"
          >
            <!-- Title -->
            <td
              style="font-family: var(--font-ui)"
              class="px-4 py-3 font-medium text-charcoal-900 dark:text-stone-100"
            >
              {{ sermon.title }}
            </td>

            <!-- Speaker -->
            <td
              style="font-family: var(--font-ui)"
              class="px-4 py-3 text-charcoal-900/70 dark:text-stone-300"
            >
              {{ sermon.speaker_name }}
            </td>

            <!-- Date -->
            <td
              style="font-family: var(--font-ui)"
              class="px-4 py-3 text-charcoal-900/60 dark:text-stone-400 tabular-nums"
            >
              {{ sermon.date }}
            </td>

            <!-- Status badge -->
            <td class="px-4 py-3">
              <span
                v-if="sermon.is_published"
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
                :to="`/sermons/${sermon.id}/edit`"
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
