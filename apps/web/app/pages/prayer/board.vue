<!--
  app/pages/prayer/board.vue — Public prayer board (route: /prayer/board)

  What it does:
    Displays the community's approved prayer requests so visitors can see
    what the congregation is praying for and join in prayer. Each card shows
    the prayer body, the submitter's name (or "Anonymous"), and the date.

    Links to /prayer for new submissions.

  Why it exists at this layer:
    The public board is the community-facing side of Phase 5b. It closes the
    loop between submission (/prayer) and visibility (this page).

  How it connects:
    - GET {apiBase}/prayer-requests → approved list (requires member auth in
      the API, but this page fetches on the client side — unauthenticated
      visitors will get a 401 and see the empty/prompt state)
    - apps/web/app/pages/prayer.vue — submission form
    - apps/admin/app/pages/prayer/index.vue — staff moderation queue
-->

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { CoContainer, CoSection } from '@churchos/ui'

useSeoMeta({
  title: 'Prayer Board — Libby Church of the Nazarene',
  description: 'Community prayer requests from Libby Church of the Nazarene.',
})

const config = useRuntimeConfig()

interface Prayer {
  id:           string
  name:         string | null
  body:         string
  is_anonymous: boolean
  prayer_count: number
  submitted_at: string | null
  is_answered:  boolean
}

const prayers  = ref<Prayer[]>([])
const loading  = ref(true)

onMounted(async () => {
  try {
    const data = await $fetch<Prayer[]>(`${config.public.apiBase}/prayer-requests`)
    prayers.value = data
  } catch {
    // Unauthenticated visitors get 401 — show empty/prompt state gracefully
    prayers.value = []
  } finally {
    loading.value = false
  }
})

function formatDate(iso: string | null): string {
  if (!iso) return ''
  return new Date(iso).toLocaleDateString('en-US', {
    month: 'short', day: 'numeric', year: 'numeric',
  })
}
</script>

<template>
  <div>
    <!-- Page header -->
    <CoSection class="bg-forest-600 dark:bg-charcoal-900 py-16">
      <CoContainer>
        <h1
          style="font-family: var(--font-display)"
          class="text-4xl md:text-5xl font-bold text-white mb-3"
        >
          Prayer Board
        </h1>
        <p
          style="font-family: var(--font-body)"
          class="text-white/70 text-lg max-w-xl"
        >
          Our community's prayer requests. Join us in lifting these needs to God.
        </p>
      </CoContainer>
    </CoSection>

    <!-- Content -->
    <CoSection>
      <CoContainer>
        <div class="max-w-2xl mx-auto">

          <!-- Submit CTA -->
          <div class="flex items-center justify-between mb-8">
            <p
              style="font-family: var(--font-ui)"
              class="text-charcoal-900/60 dark:text-stone-400 text-sm"
            >
              {{ loading ? '' : `${prayers.length} active request${prayers.length !== 1 ? 's' : ''}` }}
            </p>
            <NuxtLink
              to="/prayer"
              class="btn-primary !py-1.5 !px-4 text-sm"
              style="font-family: var(--font-ui)"
            >
              Submit a Request
            </NuxtLink>
          </div>

          <!-- Loading -->
          <p
            v-if="loading"
            style="font-family: var(--font-ui)"
            class="text-charcoal-900/50 dark:text-stone-400 text-center py-12"
          >
            Loading…
          </p>

          <!-- Empty state -->
          <div
            v-else-if="prayers.length === 0"
            class="text-center py-12"
          >
            <p
              style="font-family: var(--font-display)"
              class="text-xl font-semibold text-charcoal-900/50 dark:text-stone-400 mb-3"
            >
              No prayer requests yet
            </p>
            <p
              style="font-family: var(--font-body)"
              class="text-charcoal-900/40 dark:text-stone-500 mb-6"
            >
              Be the first to share a prayer need with our community.
            </p>
            <NuxtLink
              to="/prayer"
              class="btn-primary !px-6"
              style="font-family: var(--font-ui)"
            >
              Submit a Prayer Request
            </NuxtLink>
          </div>

          <!-- Prayer cards -->
          <div v-else class="flex flex-col gap-5">
            <div
              v-for="prayer in prayers"
              :key="prayer.id"
              data-testid="prayer-card"
              class="co-card flex flex-col gap-3"
              :class="prayer.is_answered ? 'opacity-60' : ''"
            >
              <!-- Answered badge -->
              <div v-if="prayer.is_answered" class="flex">
                <span class="badge-forest text-xs px-2 py-0.5 rounded-full">
                  Answered 🙏
                </span>
              </div>

              <!-- Prayer body -->
              <p
                style="font-family: var(--font-body)"
                class="text-charcoal-900/90 dark:text-stone-200 leading-relaxed"
              >
                {{ prayer.body }}
              </p>

              <!-- Footer -->
              <div
                class="flex items-center justify-between text-xs pt-1"
                style="font-family: var(--font-ui)"
              >
                <span class="text-charcoal-900/50 dark:text-stone-400">
                  {{ prayer.is_anonymous ? 'Anonymous' : prayer.name }}
                </span>
                <span class="text-charcoal-900/40 dark:text-stone-500">
                  {{ formatDate(prayer.submitted_at) }}
                </span>
              </div>
            </div>
          </div>

        </div>
      </CoContainer>
    </CoSection>
  </div>
</template>
