<!--
  pages/events/[id]/edit.vue — Event edit form.

  What it does:
    Loads a single event by ID, pre-fills a form, and PATCHes the changed
    fields back to the API on save.

  Why it exists at this layer:
    Nuxt 4 dynamic segment: app/pages/events/[id]/edit.vue → /events/:id/edit.
    The EventsIndexPage links each row here.

  How it connects:
    - layouts/default.vue wraps this page (sidebar + topbar)
    - middleware/auth.ts guards the route
    - $fetch GET /events/:id  — loads current data
    - $fetch PATCH /events/:id — saves edits (staff role minimum)
-->

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'

interface EventForm {
  title:                string
  description:          string
  start_at:             string
  end_at:               string
  location:             string
  is_virtual:           boolean
  virtual_url:          string
  category:             string
  recurrence:           string
  registration_required: boolean
  registration_url:     string
  is_published:         boolean
}

const route   = useRoute()
const id      = route.params.id as string

const loading = ref(true)
const saving  = ref(false)
const saved   = ref(false)
const saveErr = ref<string | null>(null)

const form = reactive<EventForm>({
  title:                '',
  description:          '',
  start_at:             '',
  end_at:               '',
  location:             '',
  is_virtual:           false,
  virtual_url:          '',
  category:             '',
  recurrence:           'none',
  registration_required: false,
  registration_url:     '',
  is_published:         false,
})

onMounted(async () => {
  try {
    const data = await $fetch<Record<string, unknown>>(`/events/${id}`)
    form.title                = (data.title                as string)  ?? ''
    form.description          = (data.description          as string)  ?? ''
    form.start_at             = (data.start_at             as string)  ?? ''
    form.end_at               = (data.end_at               as string)  ?? ''
    form.location             = (data.location             as string)  ?? ''
    form.is_virtual           = (data.is_virtual           as boolean) ?? false
    form.virtual_url          = (data.virtual_url          as string)  ?? ''
    form.category             = (data.category             as string)  ?? ''
    form.recurrence           = (data.recurrence           as string)  ?? 'none'
    form.registration_required = (data.registration_required as boolean) ?? false
    form.registration_url     = (data.registration_url     as string)  ?? ''
    form.is_published         = (data.is_published         as boolean) ?? false
  } finally {
    loading.value = false
  }
})

async function handleSubmit() {
  saving.value  = true
  saved.value   = false
  saveErr.value = null

  try {
    await $fetch(`/events/${id}`, {
      method: 'PATCH',
      body:   form,
    })
    saved.value = true
  } catch (err: unknown) {
    saveErr.value = err instanceof Error ? err.message : 'Failed to save event.'
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
        to="/events"
        style="font-family: var(--font-ui)"
        class="text-charcoal-900/50 dark:text-stone-400 hover:text-forest-500
               dark:hover:text-forest-400 text-sm transition-colors"
      >
        ← Events
      </NuxtLink>
      <span class="text-charcoal-900/20 dark:text-stone-700">/</span>
      <h1
        style="font-family: var(--font-display)"
        class="text-2xl font-semibold text-charcoal-900 dark:text-stone-50"
      >
        Edit Event
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
          placeholder="Event title"
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
          rows="3"
          style="font-family: var(--font-ui)"
          class="form-input mt-1 w-full resize-y"
          placeholder="Brief description"
        />
      </div>

      <!-- Start / End row -->
      <div class="grid grid-cols-2 gap-4">
        <div>
          <label
            for="start_at"
            style="font-family: var(--font-ui)"
            class="form-label"
          >
            Starts
          </label>
          <input
            id="start_at"
            v-model="form.start_at"
            name="start_at"
            type="datetime-local"
            style="font-family: var(--font-ui)"
            class="form-input mt-1 w-full"
          />
        </div>
        <div>
          <label
            for="end_at"
            style="font-family: var(--font-ui)"
            class="form-label"
          >
            Ends
          </label>
          <input
            id="end_at"
            v-model="form.end_at"
            name="end_at"
            type="datetime-local"
            style="font-family: var(--font-ui)"
            class="form-input mt-1 w-full"
          />
        </div>
      </div>

      <!-- Location -->
      <div>
        <label
          for="location"
          style="font-family: var(--font-ui)"
          class="form-label"
        >
          Location
        </label>
        <input
          id="location"
          v-model="form.location"
          name="location"
          type="text"
          style="font-family: var(--font-ui)"
          class="form-input mt-1 w-full"
          placeholder="Physical location"
        />
      </div>

      <!-- Category -->
      <div>
        <label
          for="category"
          style="font-family: var(--font-ui)"
          class="form-label"
        >
          Category
        </label>
        <input
          id="category"
          v-model="form.category"
          name="category"
          type="text"
          style="font-family: var(--font-ui)"
          class="form-input mt-1 w-full"
          placeholder="e.g. worship, youth, community"
        />
      </div>

      <!-- Toggles -->
      <div class="space-y-3">
        <div class="flex items-center gap-3">
          <input
            id="is_virtual"
            v-model="form.is_virtual"
            name="is_virtual"
            type="checkbox"
            class="h-4 w-4 rounded border-stone-300 text-forest-500 focus:ring-forest-500"
          />
          <label
            for="is_virtual"
            style="font-family: var(--font-ui)"
            class="text-sm text-charcoal-900 dark:text-stone-200 select-none cursor-pointer"
          >
            Virtual event
          </label>
        </div>

        <div class="flex items-center gap-3">
          <input
            id="registration_required"
            v-model="form.registration_required"
            name="registration_required"
            type="checkbox"
            class="h-4 w-4 rounded border-stone-300 text-forest-500 focus:ring-forest-500"
          />
          <label
            for="registration_required"
            style="font-family: var(--font-ui)"
            class="text-sm text-charcoal-900 dark:text-stone-200 select-none cursor-pointer"
          >
            Registration required
          </label>
        </div>

        <div class="flex items-center gap-3">
          <input
            id="is_published"
            v-model="form.is_published"
            name="is_published"
            type="checkbox"
            class="h-4 w-4 rounded border-stone-300 text-forest-500 focus:ring-forest-500"
          />
          <label
            for="is_published"
            style="font-family: var(--font-ui)"
            class="text-sm text-charcoal-900 dark:text-stone-200 select-none cursor-pointer"
          >
            Published
          </label>
        </div>
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
          to="/events"
          style="font-family: var(--font-ui)"
          class="btn-ghost px-4 py-2 text-sm"
        >
          Cancel
        </NuxtLink>
      </div>
    </form>
  </div>
</template>
