<!--
  pages/sermons/[id]/edit.vue — Sermon edit form.

  What it does:
    Loads a single sermon by ID, pre-fills a form, and PATCHes only the
    changed fields back to the API on save. Preserves all Logos-managed
    fields (duration_seconds, thumbnail_url, etc.) by using PATCH semantics.

  Why it exists at this layer:
    Nuxt 4 dynamic segments: app/pages/sermons/[id]/edit.vue maps to
    /sermons/:id/edit. The SermonsIndexPage links each row here.

  How it connects:
    - layouts/default.vue wraps this page (sidebar + topbar)
    - middleware/auth.ts guards the route
    - $fetch GET /sermons/:id  — loads current data
    - $fetch PATCH /sermons/:id — saves edits (staff role minimum)
-->

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'

interface SermonForm {
  title:               string
  speaker_name:        string
  series:              string
  date:                string
  description:         string
  scripture_reference: string
  is_published:        boolean
}

const route   = useRoute()
const id      = route.params.id as string

const loading = ref(true)
const saving  = ref(false)
const saved   = ref(false)
const saveErr = ref<string | null>(null)

const form = reactive<SermonForm>({
  title:               '',
  speaker_name:        '',
  series:              '',
  date:                '',
  description:         '',
  scripture_reference: '',
  is_published:        false,
})

onMounted(async () => {
  try {
    const data = await $fetch<Record<string, unknown>>(`/sermons/${id}`)
    form.title               = (data.title               as string)  ?? ''
    form.speaker_name        = (data.speaker_name        as string)  ?? ''
    form.series              = (data.series              as string)  ?? ''
    form.date                = (data.date                as string)  ?? ''
    form.description         = (data.description         as string)  ?? ''
    form.scripture_reference = (data.scripture_reference as string)  ?? ''
    form.is_published        = (data.is_published        as boolean) ?? false
  } finally {
    loading.value = false
  }
})

async function handleSubmit() {
  saving.value  = true
  saved.value   = false
  saveErr.value = null

  try {
    await $fetch(`/sermons/${id}`, {
      method: 'PATCH',
      body:   form,
    })
    saved.value = true
  } catch (err: unknown) {
    saveErr.value = err instanceof Error ? err.message : 'Failed to save sermon.'
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div class="max-w-2xl">
    <!-- Back + heading -->
    <div class="mb-6 flex items-center gap-3">
      <NuxtLink
        to="/sermons"
        style="font-family: var(--font-ui)"
        class="text-charcoal-900/50 dark:text-stone-400 hover:text-forest-500
               dark:hover:text-forest-400 text-sm transition-colors"
      >
        ← Sermons
      </NuxtLink>
      <span class="text-charcoal-900/20 dark:text-stone-700">/</span>
      <h1
        style="font-family: var(--font-display)"
        class="text-2xl font-semibold text-charcoal-900 dark:text-stone-50"
      >
        Edit Sermon
      </h1>
    </div>

    <!-- Loading -->
    <div
      v-if="loading"
      style="font-family: var(--font-ui)"
      class="text-charcoal-900/50 dark:text-stone-400 text-sm"
    >
      Loading…
    </div>

    <!-- Edit form -->
    <form
      v-else
      class="co-card space-y-5"
      @submit.prevent="handleSubmit"
    >
      <!-- Title -->
      <div>
        <label
          for="title"
          style="font-family: var(--font-ui)"
          class="form-label"
        >
          Title
        </label>
        <input
          id="title"
          v-model="form.title"
          name="title"
          type="text"
          required
          style="font-family: var(--font-ui)"
          class="form-input mt-1 w-full"
          placeholder="Sermon title"
        />
      </div>

      <!-- Speaker -->
      <div>
        <label
          for="speaker_name"
          style="font-family: var(--font-ui)"
          class="form-label"
        >
          Speaker
        </label>
        <input
          id="speaker_name"
          v-model="form.speaker_name"
          name="speaker_name"
          type="text"
          style="font-family: var(--font-ui)"
          class="form-input mt-1 w-full"
          placeholder="Speaker name"
        />
      </div>

      <!-- Series -->
      <div>
        <label
          for="series"
          style="font-family: var(--font-ui)"
          class="form-label"
        >
          Series
        </label>
        <input
          id="series"
          v-model="form.series"
          name="series"
          type="text"
          style="font-family: var(--font-ui)"
          class="form-input mt-1 w-full"
          placeholder="Series name (optional)"
        />
      </div>

      <!-- Date -->
      <div>
        <label
          for="date"
          style="font-family: var(--font-ui)"
          class="form-label"
        >
          Date
        </label>
        <input
          id="date"
          v-model="form.date"
          name="date"
          type="date"
          style="font-family: var(--font-ui)"
          class="form-input mt-1"
        />
      </div>

      <!-- Scripture reference -->
      <div>
        <label
          for="scripture_reference"
          style="font-family: var(--font-ui)"
          class="form-label"
        >
          Scripture Reference
        </label>
        <input
          id="scripture_reference"
          v-model="form.scripture_reference"
          name="scripture_reference"
          type="text"
          style="font-family: var(--font-ui)"
          class="form-input mt-1 w-full"
          placeholder="e.g. Romans 5:20"
        />
      </div>

      <!-- Description -->
      <div>
        <label
          for="description"
          style="font-family: var(--font-ui)"
          class="form-label"
        >
          Description
        </label>
        <textarea
          id="description"
          v-model="form.description"
          name="description"
          rows="4"
          style="font-family: var(--font-ui)"
          class="form-input mt-1 w-full resize-y"
          placeholder="Brief description of the sermon"
        />
      </div>

      <!-- Published toggle -->
      <div class="flex items-center gap-3">
        <input
          id="is_published"
          v-model="form.is_published"
          name="is_published"
          type="checkbox"
          class="h-4 w-4 rounded border-stone-300 text-forest-500
                 focus:ring-forest-500"
        />
        <label
          for="is_published"
          style="font-family: var(--font-ui)"
          class="text-sm text-charcoal-900 dark:text-stone-200 select-none cursor-pointer"
        >
          Published
        </label>
      </div>

      <!-- Feedback -->
      <p
        v-if="saved"
        style="font-family: var(--font-ui)"
        class="text-sm text-forest-600 dark:text-forest-400"
      >
        Saved successfully.
      </p>
      <p
        v-if="saveErr"
        style="font-family: var(--font-ui)"
        class="text-sm text-red-600 dark:text-red-400"
      >
        Failed to save: {{ saveErr }}
      </p>

      <!-- Actions -->
      <div class="flex items-center gap-3 pt-2">
        <button
          type="submit"
          :disabled="saving"
          style="font-family: var(--font-ui)"
          class="btn-primary px-5 py-2 text-sm disabled:opacity-50"
        >
          {{ saving ? 'Saving…' : 'Save' }}
        </button>
        <NuxtLink
          to="/sermons"
          style="font-family: var(--font-ui)"
          class="btn-ghost px-4 py-2 text-sm"
        >
          Cancel
        </NuxtLink>
      </div>
    </form>
  </div>
</template>
