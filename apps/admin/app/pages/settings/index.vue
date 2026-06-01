<!--
  pages/settings/index.vue — Admin settings page (route: /settings)

  What it does:
    Allows admin users to configure per-deployment settings stored in the
    site_config table. Sections:
      - Email Connector (Phase 6): email_provider selector (smtp | ms365),
        per-provider credential fields stored as secrets in site_config
      - AI Moderation (Phase 7): ai_provider selector (grok | gloo),
        per-provider credential fields (gloo_client_id, gloo_client_secret,
        gloo_tradition; grok_api_key for Grok fallback)
      - Prayer Board: prayer_chain_email

    Phase 10 will add an Auth Providers section (MS365 SSO, Google OAuth).

  Why it exists at this layer:
    Keeping deployment config in the admin UI (rather than env vars only)
    allows non-technical church admins to update settings without redeploying.
    Env vars remain the fallback for infrastructure-level config.

  How it connects:
    - GET /site-config/{key}   → loads current values on mount
    - PUT /site-config/{key}   → saves updated values
    - app/connectors/registry.py reads email_provider + ms365_* at send time
    - app/connectors/registry.py reads ai_provider + gloo_* at moderation time
    - app/crud/site_config.py  handles Supabase upsert
-->

<script setup lang="ts">
import { ref, onMounted } from 'vue'

definePageMeta({ middleware: 'auth' })

// --- Prayer Board ---
const prayerEmail  = ref('')
const saving       = ref(false)
const saved        = ref(false)
const saveError    = ref('')

// --- Email Connector ---
const emailProvider      = ref<'smtp' | 'ms365'>('smtp')
const ms365TenantId      = ref('')
const ms365ClientId      = ref('')
const ms365ClientSecret  = ref('')
const ms365Sender        = ref('')
const connectorSaving    = ref(false)
const connectorSaved     = ref(false)
const connectorSaveError = ref('')

// --- AI Moderation ---
const aiProvider       = ref<'grok' | 'gloo'>('grok')
const glooClientId     = ref('')
const glooClientSecret = ref('')
const glooTradition    = ref('evangelical')
const grokApiKey       = ref('')
const aiSaving         = ref(false)
const aiSaved          = ref(false)
const aiSaveError      = ref('')

onMounted(async () => {
  // Prayer chain email
  try {
    const data = await $fetch<{ value: string }>('/site-config/prayer_chain_email')
    prayerEmail.value = data?.value ?? ''
  } catch {
    prayerEmail.value = ''
  }

  // Email provider
  try {
    const data = await $fetch<{ value: string }>('/site-config/email_provider')
    emailProvider.value = (data?.value as 'smtp' | 'ms365') ?? 'smtp'
  } catch {
    emailProvider.value = 'smtp'
  }

  // MS365 credentials (masked — we load to show "configured" state, not actual values)
  try {
    const [tenant, client, sender] = await Promise.all([
      $fetch<{ value: string }>('/site-config/ms365_tenant_id').catch(() => null),
      $fetch<{ value: string }>('/site-config/ms365_client_id').catch(() => null),
      $fetch<{ value: string }>('/site-config/ms365_sender').catch(() => null),
    ])
    ms365TenantId.value = tenant?.value ?? ''
    ms365ClientId.value = client?.value ?? ''
    ms365Sender.value   = sender?.value ?? ''
    // client_secret is is_secret=true — server returns '••••••' mask; keep field blank for re-entry
  } catch {
    // MS365 not configured yet
  }

  // AI provider
  try {
    const data = await $fetch<{ value: string }>('/site-config/ai_provider')
    aiProvider.value = (data?.value as 'grok' | 'gloo') ?? 'grok'
  } catch {
    aiProvider.value = 'grok'
  }

  // Gloo credentials (loaded to show "configured" state — secrets not shown)
  try {
    const [clientId, tradition] = await Promise.all([
      $fetch<{ value: string }>('/site-config/gloo_client_id').catch(() => null),
      $fetch<{ value: string }>('/site-config/gloo_tradition').catch(() => null),
    ])
    glooClientId.value  = clientId?.value  ?? ''
    glooTradition.value = tradition?.value ?? 'evangelical'
    // gloo_client_secret is is_secret=true — keep field blank for re-entry
  } catch {
    // Gloo not configured yet
  }
})

async function handleSave() {
  saving.value    = true
  saved.value     = false
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

async function handleAiSave() {
  aiSaving.value    = true
  aiSaved.value     = false
  aiSaveError.value = ''
  try {
    await $fetch('/site-config/ai_provider', {
      method: 'PUT',
      body:   { value: aiProvider.value, is_secret: false },
    })
    if (aiProvider.value === 'gloo') {
      await Promise.all([
        $fetch('/site-config/gloo_client_id', {
          method: 'PUT',
          body:   { value: glooClientId.value, is_secret: false },
        }),
        glooClientSecret.value
          ? $fetch('/site-config/gloo_client_secret', {
              method: 'PUT',
              body:   { value: glooClientSecret.value, is_secret: true },
            })
          : Promise.resolve(),
        $fetch('/site-config/gloo_tradition', {
          method: 'PUT',
          body:   { value: glooTradition.value, is_secret: false },
        }),
      ])
    } else if (aiProvider.value === 'grok' && grokApiKey.value) {
      await $fetch('/site-config/grok_api_key', {
        method: 'PUT',
        body:   { value: grokApiKey.value, is_secret: true },
      })
    }
    aiSaved.value = true
  } catch {
    aiSaveError.value = 'Failed to save AI moderation settings. Please try again.'
  } finally {
    aiSaving.value = false
  }
}

async function handleConnectorSave() {
  connectorSaving.value    = true
  connectorSaved.value     = false
  connectorSaveError.value = ''
  try {
    await $fetch('/site-config/email_provider', {
      method: 'PUT',
      body:   { value: emailProvider.value, is_secret: false },
    })
    if (emailProvider.value === 'ms365') {
      await Promise.all([
        $fetch('/site-config/ms365_tenant_id', {
          method: 'PUT',
          body:   { value: ms365TenantId.value, is_secret: false },
        }),
        $fetch('/site-config/ms365_client_id', {
          method: 'PUT',
          body:   { value: ms365ClientId.value, is_secret: false },
        }),
        ms365ClientSecret.value
          ? $fetch('/site-config/ms365_client_secret', {
              method: 'PUT',
              body:   { value: ms365ClientSecret.value, is_secret: true },
            })
          : Promise.resolve(),
        $fetch('/site-config/ms365_sender', {
          method: 'PUT',
          body:   { value: ms365Sender.value, is_secret: false },
        }),
      ])
    }
    connectorSaved.value = true
  } catch {
    connectorSaveError.value = 'Failed to save connector settings. Please try again.'
  } finally {
    connectorSaving.value = false
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

    <!-- Email Connector section -->
    <div class="co-card mb-6" data-testid="connector-section">
      <h2
        style="font-family: var(--font-display)"
        class="text-lg font-semibold text-charcoal-900 dark:text-stone-50 mb-1"
      >
        Email Connector
      </h2>
      <p
        style="font-family: var(--font-ui)"
        class="text-sm text-charcoal-900/50 dark:text-stone-400 mb-5"
      >
        Choose how ChurchOS sends emails. SMTP works with any email provider
        using credentials from your environment variables. MS365 uses the
        Microsoft Graph API with your Azure app registration.
      </p>

      <form class="flex flex-col gap-4 max-w-md" data-testid="connector-form" @submit.prevent="handleConnectorSave">
        <!-- Provider selector -->
        <div class="flex flex-col gap-1">
          <label
            for="email_provider"
            class="form-label"
            style="font-family: var(--font-ui)"
          >
            Email Provider
          </label>
          <select
            id="email_provider"
            v-model="emailProvider"
            class="form-input"
            style="font-family: var(--font-ui)"
            data-testid="email-provider-select"
          >
            <option value="smtp">SMTP (default)</option>
            <option value="ms365">Microsoft 365 (Graph API)</option>
          </select>
        </div>

        <!-- MS365 credential fields — shown only when ms365 is selected -->
        <template v-if="emailProvider === 'ms365'">
          <div class="flex flex-col gap-1">
            <label for="ms365_tenant_id" class="form-label" style="font-family: var(--font-ui)">
              Tenant ID
            </label>
            <input
              id="ms365_tenant_id"
              v-model="ms365TenantId"
              class="form-input"
              style="font-family: var(--font-ui)"
              placeholder="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
              data-testid="ms365-tenant-id"
            />
          </div>
          <div class="flex flex-col gap-1">
            <label for="ms365_client_id" class="form-label" style="font-family: var(--font-ui)">
              Client (Application) ID
            </label>
            <input
              id="ms365_client_id"
              v-model="ms365ClientId"
              class="form-input"
              style="font-family: var(--font-ui)"
              placeholder="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
              data-testid="ms365-client-id"
            />
          </div>
          <div class="flex flex-col gap-1">
            <label for="ms365_client_secret" class="form-label" style="font-family: var(--font-ui)">
              Client Secret
            </label>
            <input
              id="ms365_client_secret"
              v-model="ms365ClientSecret"
              type="password"
              class="form-input"
              style="font-family: var(--font-ui)"
              placeholder="Leave blank to keep existing secret"
              data-testid="ms365-client-secret"
            />
            <p class="text-xs text-charcoal-900/40 dark:text-stone-500" style="font-family: var(--font-ui)">
              Stored encrypted. Leave blank to keep the current value.
            </p>
          </div>
          <div class="flex flex-col gap-1">
            <label for="ms365_sender" class="form-label" style="font-family: var(--font-ui)">
              Sender Email Address
            </label>
            <input
              id="ms365_sender"
              v-model="ms365Sender"
              type="email"
              class="form-input"
              style="font-family: var(--font-ui)"
              placeholder="noreply@yourdomain.org"
              data-testid="ms365-sender"
            />
            <p class="text-xs text-charcoal-900/40 dark:text-stone-500" style="font-family: var(--font-ui)">
              Must be a licensed mailbox in your Microsoft 365 tenant.
            </p>
          </div>
        </template>

        <!-- SMTP hint -->
        <p
          v-if="emailProvider === 'smtp'"
          class="text-sm text-charcoal-900/50 dark:text-stone-400"
          style="font-family: var(--font-ui)"
        >
          SMTP credentials are configured via environment variables:
          <code class="text-xs bg-stone-100 dark:bg-charcoal-800 px-1 rounded">
            SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD
          </code>
        </p>

        <!-- Feedback -->
        <p
          v-show="connectorSaved"
          class="text-sm text-forest-600 dark:text-forest-300"
          style="font-family: var(--font-ui)"
          data-testid="connector-saved"
        >
          Connector settings saved.
        </p>
        <p
          v-show="connectorSaveError"
          class="text-sm text-red-600 dark:text-red-400"
          style="font-family: var(--font-ui)"
          data-testid="connector-error"
        >
          {{ connectorSaveError }}
        </p>

        <div>
          <button
            type="submit"
            class="btn-primary !py-1.5 !px-6 text-sm"
            style="font-family: var(--font-ui)"
            :disabled="connectorSaving"
            data-testid="connector-save-btn"
          >
            {{ connectorSaving ? 'Saving…' : 'Save Connector Settings' }}
          </button>
        </div>
      </form>
    </div>

    <!-- AI Moderation section -->
    <div class="co-card mb-6" data-testid="ai-moderation-section">
      <h2
        style="font-family: var(--font-display)"
        class="text-lg font-semibold text-charcoal-900 dark:text-stone-50 mb-1"
      >
        AI Moderation
      </h2>
      <p
        style="font-family: var(--font-ui)"
        class="text-sm text-charcoal-900/50 dark:text-stone-400 mb-5"
      >
        Choose how ChurchOS moderates prayer submissions before they appear on
        the board. Gloo AI understands faith-community language. Grok (xAI) is
        the fallback. If neither is configured, all submissions are approved.
      </p>

      <form class="flex flex-col gap-4 max-w-md" data-testid="ai-moderation-form" @submit.prevent="handleAiSave">
        <!-- Provider selector -->
        <div class="flex flex-col gap-1">
          <label for="ai_provider" class="form-label" style="font-family: var(--font-ui)">
            AI Provider
          </label>
          <select
            id="ai_provider"
            v-model="aiProvider"
            class="form-input"
            style="font-family: var(--font-ui)"
            data-testid="ai-provider-select"
          >
            <option value="grok">Grok by xAI (default)</option>
            <option value="gloo">Gloo Faith AI (primary)</option>
          </select>
        </div>

        <!-- Grok API key — shown when grok is selected -->
        <template v-if="aiProvider === 'grok'">
          <div class="flex flex-col gap-1">
            <label for="grok_api_key" class="form-label" style="font-family: var(--font-ui)">
              Grok API Key
            </label>
            <input
              id="grok_api_key"
              v-model="grokApiKey"
              type="password"
              class="form-input"
              style="font-family: var(--font-ui)"
              placeholder="Leave blank to keep existing key"
              data-testid="grok-api-key"
            />
            <p class="text-xs text-charcoal-900/40 dark:text-stone-500" style="font-family: var(--font-ui)">
              Stored encrypted. Free tier available at
              <a href="https://console.x.ai" target="_blank" class="underline">console.x.ai</a>.
              Leave blank to keep the current value.
            </p>
          </div>
        </template>

        <!-- Gloo credential fields — shown when gloo is selected -->
        <template v-if="aiProvider === 'gloo'">
          <div class="flex flex-col gap-1">
            <label for="gloo_client_id" class="form-label" style="font-family: var(--font-ui)">
              Client ID
            </label>
            <input
              id="gloo_client_id"
              v-model="glooClientId"
              class="form-input"
              style="font-family: var(--font-ui)"
              placeholder="Gloo API client ID"
              data-testid="gloo-client-id"
            />
          </div>
          <div class="flex flex-col gap-1">
            <label for="gloo_client_secret" class="form-label" style="font-family: var(--font-ui)">
              Client Secret
            </label>
            <input
              id="gloo_client_secret"
              v-model="glooClientSecret"
              type="password"
              class="form-input"
              style="font-family: var(--font-ui)"
              placeholder="Leave blank to keep existing secret"
              data-testid="gloo-client-secret"
            />
            <p class="text-xs text-charcoal-900/40 dark:text-stone-500" style="font-family: var(--font-ui)">
              Stored encrypted. Leave blank to keep the current value.
            </p>
          </div>
          <div class="flex flex-col gap-1">
            <label for="gloo_tradition" class="form-label" style="font-family: var(--font-ui)">
              Theological Tradition
            </label>
            <input
              id="gloo_tradition"
              v-model="glooTradition"
              class="form-input"
              style="font-family: var(--font-ui)"
              placeholder="evangelical"
              data-testid="gloo-tradition"
            />
            <p class="text-xs text-charcoal-900/40 dark:text-stone-500" style="font-family: var(--font-ui)">
              Sent to Gloo to apply faith-context moderation. Examples:
              <code class="text-xs bg-stone-100 dark:bg-charcoal-800 px-1 rounded">evangelical</code>,
              <code class="text-xs bg-stone-100 dark:bg-charcoal-800 px-1 rounded">catholic</code>,
              <code class="text-xs bg-stone-100 dark:bg-charcoal-800 px-1 rounded">mainline</code>
            </p>
          </div>
        </template>

        <!-- Feedback -->
        <p
          v-show="aiSaved"
          class="text-sm text-forest-600 dark:text-forest-300"
          style="font-family: var(--font-ui)"
          data-testid="ai-moderation-saved"
        >
          AI moderation settings saved.
        </p>
        <p
          v-show="aiSaveError"
          class="text-sm text-red-600 dark:text-red-400"
          style="font-family: var(--font-ui)"
          data-testid="ai-moderation-error"
        >
          {{ aiSaveError }}
        </p>

        <div>
          <button
            type="submit"
            class="btn-primary !py-1.5 !px-6 text-sm"
            style="font-family: var(--font-ui)"
            :disabled="aiSaving"
            data-testid="ai-moderation-save-btn"
          >
            {{ aiSaving ? 'Saving…' : 'Save AI Settings' }}
          </button>
        </div>
      </form>
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

      <form class="flex flex-col gap-4 max-w-md" data-testid="prayer-form" @submit.prevent="handleSave">
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
