<!--
  app/pages/sermons/index.vue — Sermons listing (route: /sermons)

  What it does:
    Lists sermon cards with title, speaker, scripture reference, series badge,
    and date. Content is static placeholder data for Phase 2 — real sermons
    will be fetched from the API (useFetch) in Phase 4 after the admin CRUD
    endpoints are built.

  Why it exists at this layer:
    Sermons are the primary content offering. The static page establishes the
    correct URL, component structure, and test contracts before the API exists.

  How it connects:
    - Rendered inside app/layouts/default.vue
    - Uses @churchos/ui for all card and badge rendering
    - Will be upgraded to useFetch + server-side rendering in Phase 4
-->

<script setup lang="ts">
import {
  CoBadge,
  CoContainer,
  CoSection,
} from '@churchos/ui'

useSeoMeta({
  title: 'Sermons — Libby Church of the Nazarene',
  description: 'Listen to recent sermons from Libby Church of the Nazarene.',
})

// Placeholder sermon data — replaced with API fetch in Phase 4
const sermons = [
  {
    id: 1,
    title: 'Walking by Faith in Uncertain Times',
    speaker: 'Pastor John Smith',
    scripture: 'Hebrews 11:1–6',
    series: 'Faith & Courage',
    date: 'May 18, 2025',
    featured: true,
  },
  {
    id: 2,
    title: 'The Peace That Passes Understanding',
    speaker: 'Pastor John Smith',
    scripture: 'Philippians 4:4–7',
    series: 'Faith & Courage',
    date: 'May 11, 2025',
    featured: false,
  },
  {
    id: 3,
    title: 'Rooted and Built Up in Him',
    speaker: 'Pastor John Smith',
    scripture: 'Colossians 2:6–7',
    series: 'Rooted',
    date: 'May 4, 2025',
    featured: false,
  },
  {
    id: 4,
    title: 'The Vine and the Branches',
    speaker: 'Guest Speaker',
    scripture: 'John 15:1–8',
    series: 'Rooted',
    date: 'April 27, 2025',
    featured: false,
  },
  {
    id: 5,
    title: 'He Is Risen — Now What?',
    speaker: 'Pastor John Smith',
    scripture: 'Luke 24:13–35',
    series: 'Easter 2025',
    date: 'April 20, 2025',
    featured: false,
  },
  {
    id: 6,
    title: 'Good Friday: The Suffering Servant',
    speaker: 'Pastor John Smith',
    scripture: 'Isaiah 53',
    series: 'Easter 2025',
    date: 'April 18, 2025',
    featured: false,
  },
]
</script>

<template>
  <!-- Page header -->
  <CoSection class="bg-forest-600 dark:bg-charcoal-900 py-16">
    <CoContainer>
      <h1
        style="font-family: var(--font-display)"
        class="text-4xl md:text-5xl font-bold text-white mb-3"
      >
        Sermons
      </h1>
      <p
        style="font-family: var(--font-body)"
        class="text-white/70 text-lg max-w-xl"
      >
        Teaching from God's Word every Sunday morning. Listen online or join us
        in person.
      </p>
    </CoContainer>
  </CoSection>

  <!-- Sermon grid -->
  <CoSection>
    <CoContainer>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div
          v-for="sermon in sermons"
          :key="sermon.id"
          data-testid="sermon-card"
          class="co-card flex flex-col gap-3"
        >
          <!-- Badges -->
          <div class="flex flex-wrap gap-2">
            <CoBadge v-if="sermon.featured" color="gold">Featured</CoBadge>
            <CoBadge color="kootenai" data-testid="sermon-series">
              {{ sermon.series }}
            </CoBadge>
          </div>

          <!-- Title -->
          <h3
            data-testid="sermon-title"
            style="font-family: var(--font-display)"
            class="text-lg font-semibold text-charcoal-900 dark:text-stone-50 leading-snug"
          >
            {{ sermon.title }}
          </h3>

          <!-- Scripture -->
          <p
            style="font-family: var(--font-body)"
            class="text-forest-600 dark:text-forest-300 text-sm italic"
          >
            {{ sermon.scripture }}
          </p>

          <!-- Meta -->
          <div
            style="font-family: var(--font-ui)"
            class="mt-auto pt-2 border-t border-stone-200 dark:border-charcoal-700 flex justify-between text-xs text-charcoal-900/50 dark:text-stone-400"
          >
            <span data-testid="sermon-speaker">{{ sermon.speaker }}</span>
            <span>{{ sermon.date }}</span>
          </div>
        </div>
      </div>
    </CoContainer>
  </CoSection>
</template>
