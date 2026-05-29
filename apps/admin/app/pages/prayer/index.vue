<!--
  pages/prayer/index.vue — Prayer request moderation queue (route: /prayer)

  What it does:
    Lists all pending prayer requests fetched from GET /prayer-requests/pending.
    Staff can approve or reject each request. Actioned rows are removed from
    the queue immediately for a clean workflow.

  Why it exists at this layer:
    The moderation queue is the staff-facing side of the Phase 5 prayer board.
    Staff need a clear, actionable view of submissions before they go public.

  How it connects:
    - layouts/default.vue wraps this page (sidebar + topbar)
    - GET /prayer-requests/pending → fetches pending submissions (staff+)
    - PATCH /prayer-requests/{id} → approves or rejects a submission
    - apps/web/app/pages/prayer.vue is the public submission form
-->

<script setup lang="ts">
import { ref, onMounted } from 'vue'

interface PrayerRequest {
  id:           string
  name:         string | null
  body:         string
  is_anonymous: boolean
  status:       string
  ai_score:     number | null
  submitted_at: string | null
}

definePageMeta({ middleware: 'auth' })

const queue    = ref<PrayerRequest[]>([])
const loading  = ref(true)
const actionErr = ref<string | null>(null)

onMounted(async () => {
  try {
    const data = await $fetch<PrayerRequest[]>('/prayer-requests/pending')
    queue.value = data
  } catch {
    actionErr.value = 'Failed to load prayer queue.'
  } finally {
    loading.value = false
  }
})

async function moderate(id: string, status: 'approved' | 'rejected') {
  actionErr.value = null
  try {
    await $fetch(`/prayer-requests/${id}`, {
      method: 'PATCH',
      body:   { status },
    })
    // Remove actioned row from the local queue immediately
    queue.value = queue.value.filter(p => p.id !== id)
  } catch {
    actionErr.value = 'Action failed. Please try again.'
  }
}
</script>

<template>
  <div>
    <!-- Page header -->
    <div class="mb-6 flex items-center justify-between">
      <h1
        style="font-family: var(--font-display)"
        class="text-2xl font-bold text-charcoal-900 dark:text-stone-50"
      >
        Prayer Queue
      </h1>
      <span
        style="font-family: var(--font-ui)"
        class="text-sm text-charcoal-900/50 dark:text-stone-400"
      >
        Pending: {{ queue.length }}
      </span>
    </div>

    <!-- Error banner -->
    <div
      v-show="actionErr"
      class="mb-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded text-red-700 dark:text-red-300 text-sm"
      style="font-family: var(--font-ui)"
    >
      {{ actionErr }}
    </div>

    <!-- Loading -->
    <p
      v-if="loading"
      style="font-family: var(--font-ui)"
      class="text-charcoal-900/50 dark:text-stone-400"
    >
      Loading…
    </p>

    <!-- Empty state -->
    <div
      v-else-if="queue.length === 0"
      class="co-card text-center py-12"
    >
      <p
        style="font-family: var(--font-display)"
        class="text-xl font-semibold text-forest-600 dark:text-forest-300 mb-2"
      >
        All caught up!
      </p>
      <p
        style="font-family: var(--font-ui)"
        class="text-charcoal-900/50 dark:text-stone-400"
      >
        No pending prayer requests.
      </p>
    </div>

    <!-- Queue list -->
    <div
      v-else
      class="flex flex-col gap-4"
    >
      <div
        v-for="prayer in queue"
        :key="prayer.id"
        data-testid="prayer-row"
        class="co-card flex flex-col gap-3"
      >
        <!-- Submitter + meta -->
        <div class="flex items-center justify-between gap-2">
          <span
            style="font-family: var(--font-ui)"
            class="text-sm font-medium text-charcoal-900 dark:text-stone-200"
          >
            {{ prayer.is_anonymous ? 'Anonymous' : (prayer.name || 'Unknown') }}
          </span>
          <div class="flex items-center gap-2">
            <span
              v-if="prayer.ai_score !== null"
              style="font-family: var(--font-ui)"
              class="text-xs text-charcoal-900/40 dark:text-stone-500"
            >
              AI {{ Math.round((prayer.ai_score ?? 0) * 100) }}%
            </span>
            <span
              style="font-family: var(--font-ui)"
              class="text-xs text-charcoal-900/40 dark:text-stone-500"
            >
              {{ prayer.submitted_at ? new Date(prayer.submitted_at).toLocaleDateString() : '—' }}
            </span>
          </div>
        </div>

        <!-- Prayer body -->
        <p
          style="font-family: var(--font-body)"
          class="text-charcoal-900/80 dark:text-stone-300 leading-relaxed"
        >
          {{ prayer.body }}
        </p>

        <!-- Actions -->
        <div class="flex items-center gap-3 pt-1">
          <button
            data-testid="btn-approve"
            class="btn-primary !py-1.5 !px-4 text-sm"
            style="font-family: var(--font-ui)"
            @click="moderate(prayer.id, 'approved')"
          >
            Approve
          </button>
          <button
            data-testid="btn-reject"
            class="btn-ghost !py-1.5 !px-4 text-sm text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20"
            style="font-family: var(--font-ui)"
            @click="moderate(prayer.id, 'rejected')"
          >
            Reject
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
