<!--
  pages/settings/index.vue — Admin settings page (route: /settings)

  What it does:
    Allows admin users to configure per-deployment settings stored in the
    site_config table. Currently exposes:
      - prayer_chain_email: the email address notified when a prayer request
        is approved

    Phase 6 will expand this page with connector configuration (SMTP, MS365,
    Google Workspace, etc.) and Phase 10 will add auth provider settings.

  Why it exists at this layer:
    Keeping deployment configuration in the admin UI (rather than env vars
    only) allows non-technical church admins to update settings without
    redeploying. Env vars remain the fallback for infrastructure-level config.

  How it connects:
    - GET /site-config/prayer_chain_email → loads current value on mount
    - PUT /site-config/prayer_chain_email → saves updated value
    - app/crud/site_config.py handles Supabase upsert
    - app/services/email.py reads prayer_chain_email at send time
-->

<script setup lang="ts">
import { ref, onMounted } from 'vue'

definePageMeta({ middleware: 'auth' })

const prayerEmail  = ref('')
const saving       = ref(false)
const saved        = ref(false)
const saveError    = ref('')

onMounted(async () => {
  try {
    const data = await $fetch<{ value: string }>('/site-config/prayer_chain_email')
    prayerEmail.value = data?.value ?? ''
  } catch {
    // Key doesn't exist yet — start with empty field
    prayerEmail.value = ''
  }
})

async function handleSave() {
  saving.value   = true
  saved.value    = false
  saveError.value = ''

  try {
    await $fetch('/site-config/prayer_chain_email', {
      method: 'PUT',
      body:   { value: prayerEmail.value, is_secret: false },
    })
    saved.value = true
  } catch {
    saveError.value = 'Failed to save settings. Please try again.'
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div>
    <!-- Page header -->
    <div class="mb-6">
      <h1
        style="font-family: var(--font-display)"
        class="text-2xl font-bold text-charcoal-900 dark:text-stone-50"
      >
        Settings
      </h1>
      <p
        style="font-family: var(--font-ui)"
        class="text-sm text-charcoal-900/50 dark:text-stone-400 mt-1"
      >
        Deployment configuration for this ChurchOS installation.
      </p>
    </div>

    <!-- Prayer Board section -->
    <div class="co-card mb-6">
      <h2
        style="font-family: var(--font-display)"
        class="text-lg font-semibold text-charcoal-900 dark:text-stone-50 mb-1"
      >
        Prayer Board
      </h2>
      <p
        style="font-family: var(--font-ui)"
        class="text-sm text-charcoal-900/50 dark:text-stone-400 mb-5"
      >
        When a prayer request is approved, a notification is sent to the
        prayer chain email address below.
      </p>

      <form class="flex flex-col gap-4 max-w-md" @submit.prevent="handleSave">
        <!-- Prayer chain email -->
        <div class="flex flex-col gap-1">
          <label
            for="prayer_chain_email"
            class="form-label"
            style="font-family: var(--font-ui)"
          >
            Prayer Chain Email
          </label>
          <input
            id="prayer_chain_email"
            v-model="prayerEmail"
            name="prayer_chain_email"
            type="email"
            class="form-input"
            style="font-family: var(--font-ui)"
            placeholder="prayer@yourdomain.org"
          />
          <p
            style="font-family: var(--font-ui)"
            class="text-xs text-charcoal-900/40 dark:text-stone-500"
          >
            Can be a distribution list or individual address. Leave blank to
            disable email notifications.
          </p>
        </div>

        <!-- Feedback -->
        <p
          v-show="saved"
          class="text-sm text-forest-600 dark:text-forest-300"
          style="font-family: var(--font-ui)"
        >
          Settings saved successfully.
        </p>
        <p
          v-show="saveError"
          class="text-sm text-red-600 dark:text-red-400"
          style="font-family: var(--font-ui)"
        >
          {{ saveError }}
        </p>

        <div>
          <button
            type="submit"
            class="btn-primary !py-1.5 !px-6 text-sm"
            style="font-family: var(--font-ui)"
            :disabled="saving"
          >
            {{ saving ? 'Saving…' : 'Save Settings' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>
