<!--
  app/pages/prayer/index.vue — Public prayer request submission form (route: /prayer)

  What it does:
    Lets any visitor submit a prayer request to the church community.
    Submissions go to POST /prayer-requests on the API, which applies
    Redis rate limiting and Grok AI moderation before storing.

    States: idle → submitting → success | error

    The anonymous checkbox hides the name field and sets is_anonymous=true
    on the payload. Email is always optional and shown as a subtle field
    (for follow-up, never displayed publicly).

  Why it exists at this layer:
    Phase 5 public-facing component. The prayer board is the community's
    primary spiritual engagement feature beyond sermons and events.

  Why index.vue instead of prayer.vue:
    Nuxt 4 treats a file named prayer.vue as a parent layout for all routes
    under /prayer/*, which caused /prayer/board to render the form instead
    of the board. Moving to prayer/index.vue makes /prayer the index route
    of the directory without interfering with sibling routes.

  How it connects:
    - POST {runtimeConfig.public.apiBase}/prayer-requests
    - apps/api/app/routers/prayer_requests.py handles the request
    - apps/web/app/pages/prayer/board.vue — the public prayer board
    - apps/admin/app/pages/prayer/index.vue shows the moderation queue
-->

<script setup lang="ts">
import { ref, computed } from 'vue'
import { CoFormInput, CoButton, CoContainer, CoSection } from '@churchos/ui'

useSeoMeta({
  title: 'Prayer Board — Libby Church of the Nazarene',
  description: 'Submit a prayer request to the Libby Church of the Nazarene community.',
})

const config = useRuntimeConfig()

const form = ref({
  body:         '',
  name:         '',
  email:        '',
  is_anonymous: false,
})

const submitting = ref(false)
const submitted  = ref(false)
const error      = ref('')

const isAnonymous = computed(() => form.value.is_anonymous)

async function handleSubmit() {
  error.value    = ''
  submitting.value = true

  const payload: Record<string, unknown> = {
    body:         form.value.body,
    is_anonymous: form.value.is_anonymous,
  }
  if (!form.value.is_anonymous && form.value.name.trim()) {
    payload.name = form.value.name.trim()
  }
  if (form.value.email.trim()) {
    payload.email = form.value.email.trim()
  }

  try {
    await $fetch(`${config.public.apiBase}/prayer-requests`, {
      method: 'POST',
      body:   payload,
    })
    submitted.value = true
  } catch {
    error.value = 'Something went wrong. Please try again.'
  } finally {
    submitting.value = false
  }
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
        Share your prayer needs with our community. Every request is received
        with care and lifted up in prayer.
      </p>
    </CoContainer>
  </CoSection>

  <!-- Form section -->
  <CoSection>
    <CoContainer>
      <div class="max-w-xl mx-auto">

        <!-- Success state — v-show keeps element in DOM, avoids fragment removal -->
        <div
          v-show="submitted"
          class="co-card border-forest-300 dark:border-forest-700 text-center py-12"
          data-testid="success-message"
        >
          <p
            style="font-family: var(--font-display)"
            class="text-2xl font-semibold text-forest-600 dark:text-forest-300 mb-3"
          >
            Prayer Request Submitted
          </p>
          <p
            style="font-family: var(--font-body)"
            class="text-charcoal-900/70 dark:text-stone-300"
          >
            Thank you for sharing. Our community will be praying for you.
          </p>
        </div>

        <!-- Form — v-show keeps it in DOM during transition -->
        <form
          v-show="!submitted"
          class="flex flex-col gap-5"
          novalidate
          @submit.prevent="handleSubmit"
        >
          <!-- Prayer request body -->
          <div class="flex flex-col gap-1">
            <label
              for="body"
              class="form-label"
              style="font-family: var(--font-ui)"
            >
              Prayer Request <span class="text-red-500">*</span>
            </label>
            <textarea
              id="body"
              v-model="form.body"
              name="body"
              rows="5"
              placeholder="Share what's on your heart…"
              class="form-input resize-y"
              style="font-family: var(--font-body)"
              required
            />
          </div>

          <!-- Anonymous toggle -->
          <label
            class="flex items-center gap-3 cursor-pointer"
            style="font-family: var(--font-ui)"
          >
            <input
              v-model="form.is_anonymous"
              type="checkbox"
              class="w-4 h-4 accent-forest-500"
            />
            <span class="text-charcoal-900/80 dark:text-stone-300 text-sm">
              Submit anonymously
            </span>
          </label>

          <!-- Name — v-show keeps input in DOM; hidden via CSS when anonymous -->
          <div v-show="!isAnonymous">
            <CoFormInput
              id="name"
              v-model="form.name"
              label="Your name (optional)"
              name="name"
              placeholder="Jane Smith"
            />
          </div>

          <!-- Email — always optional -->
          <CoFormInput
            id="email"
            v-model="form.email"
            label="Email address (optional — for follow-up only)"
            name="email"
            type="email"
            placeholder="jane@example.com"
          />

          <!-- Error message -->
          <p
            v-show="error"
            class="text-red-600 dark:text-red-400 text-sm"
            style="font-family: var(--font-ui)"
            data-testid="error-message"
          >
            {{ error }}
          </p>

          <CoButton
            variant="primary"
            tag="button"
            type="submit"
            class="self-start !px-8"
            :disabled="submitting || !form.body.trim()"
          >
            {{ submitting ? 'Submitting…' : 'Submit Prayer Request' }}
          </CoButton>
        </form>

      </div>
    </CoContainer>
  </CoSection>
  </div>
</template>
