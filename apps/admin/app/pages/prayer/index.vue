<!--
  pages/prayer/index.vue — Prayer request moderation queue (route: /prayer)

  What it does:
    Two-tab interface for managing prayer requests:
      Pending — newly submitted requests awaiting approval or rejection
      Active  — approved requests; staff can mark them as answered

  How it connects:
    - GET /prayer-requests/pending → pending tab
    - GET /prayer-requests?status=approved → active tab (approved, not yet answered)
    - PATCH /prayer-requests/{id} → approve or reject
    - PATCH /prayer-requests/{id}/answered → mark as answered
-->

<script setup lang="ts">
import { ref, onMounted } from 'vue'

interface PrayerRequest {
  id:           string
  name:         string | null
  body:         string
  is_anonymous: boolean
  status:       string
  is_answered:  boolean
  ai_score:     number | null
  submitted_at: string | null
}

definePageMeta({ middleware: 'auth' })

type Tab = 'pending' | 'active'
const activeTab  = ref<Tab>('pending')
const pending    = ref<PrayerRequest[]>([])
const active     = ref<PrayerRequest[]>([])
const loading    = ref(true)
const actionErr  = ref<string | null>(null)

async function loadPending() {
  const data = await $fetch<PrayerRequest[]>('/prayer-requests/pending')
  pending.value = data
}

async function loadActive() {
  const data = await $fetch<PrayerRequest[]>('/prayer-requests')
  active.value = data.filter((p: PrayerRequest) => !p.is_answered)
}

onMounted(async () => {
  try {
    await loadPending()
  } catch {
    actionErr.value = 'Failed to load prayer queue.'
  } finally {
    loading.value = false
  }
})

async function switchTab(tab: Tab) {
  activeTab.value = tab
  actionErr.value = null
  loading.value = true
  try {
    if (tab === 'pending') await loadPending()
    else await loadActive()
  } catch {
    actionErr.value = 'Failed to load requests.'
  } finally {
    loading.value = false
  }
}

async function moderate(id: string, status: 'approved' | 'rejected') {
  actionErr.value = null
  try {
    await $fetch(`/prayer-requests/${id}`, {
      method: 'PATCH',
      body:   { status },
    })
    pending.value = pending.value.filter(p => p.id !== id)
  } catch {
    actionErr.value = 'Action failed. Please try again.'
  }
}

async function markAnswered(id: string) {
  actionErr.value = null
  try {
    await $fetch(`/prayer-requests/${id}/answered`, {
      method: 'PATCH',
      body:   { is_answered: true },
    })
    active.value = active.value.filter(p => p.id !== id)
  } catch {
    actionErr.value = 'Action failed. Please try again.'
  }
}

const currentQueue = ref<PrayerRequest[]>([])
import { watch } from 'vue'
watch(activeTab, () => {
  currentQueue.value = activeTab.value === 'pending' ? pending.value : active.value
})
watch(pending, (v) => { if (activeTab.value === 'pending') currentQueue.value = v }, { deep: true })
watch(active,  (v) => { if (activeTab.value === 'active')  currentQueue.value = v }, { deep: true })
onMounted(() => { currentQueue.value = pending.value })
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
    </div>

    <!-- Tabs -->
    <div class="flex gap-1 mb-5 border-b border-stone-200 dark:border-stone-700">
      <button
        data-testid="tab-pending"
        style="font-family: var(--font-ui)"
        class="px-4 py-2 text-sm font-medium transition-colors border-b-2 -mb-px"
        :class="activeTab === 'pending'
          ? 'border-forest-500 text-forest-600 dark:text-forest-300'
          : 'border-transparent text-charcoal-900/50 dark:text-stone-400 hover:text-charcoal-900 dark:hover:text-stone-200'"
        @click="switchTab('pending')"
      >
        Pending
        <span
          v-if="pending.length"
          class="ml-1.5 badge-gold text-xs px-1.5 py-0.5 rounded-full"
        >{{ pending.length }}</span>
      </button>
      <button
        data-testid="tab-active"
        style="font-family: var(--font-ui)"
        class="px-4 py-2 text-sm font-medium transition-colors border-b-2 -mb-px"
        :class="activeTab === 'active'
          ? 'border-forest-500 text-forest-600 dark:text-forest-300'
          : 'border-transparent text-charcoal-900/50 dark:text-stone-400 hover:text-charcoal-900 dark:hover:text-stone-200'"
        @click="switchTab('active')"
      >
        Active
      </button>
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
      v-else-if="currentQueue.length === 0"
      class="co-card text-center py-12"
    >
      <p
        style="font-family: var(--font-display)"
        class="text-xl font-semibold text-forest-600 dark:text-forest-300 mb-2"
      >
        {{ activeTab === 'pending' ? 'All caught up!' : 'No active requests' }}
      </p>
      <p
        style="font-family: var(--font-ui)"
        class="text-charcoal-900/50 dark:text-stone-400"
      >
        {{ activeTab === 'pending' ? 'No pending prayer requests.' : 'All prayers have been answered or are pending.' }}
      </p>
    </div>

    <!-- Queue list -->
    <div v-else class="flex flex-col gap-4">
      <div
        v-for="prayer in currentQueue"
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

        <!-- Actions — pending tab -->
        <div v-if="activeTab === 'pending'" class="flex items-center gap-3 pt-1">
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

        <!-- Actions — active tab -->
        <div v-else class="flex items-center gap-3 pt-1">
          <button
            data-testid="btn-answered"
            class="btn-primary !py-1.5 !px-4 text-sm"
            style="font-family: var(--font-ui)"
            @click="markAnswered(prayer.id)"
          >
            Mark Answered
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
