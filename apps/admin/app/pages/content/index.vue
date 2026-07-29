<!--
  pages/content/index.vue — Site content CMS page (route: /content)

  What it does:
    Lets staff+ edit the site-content keys stored in site_config (church
    identity, location, contact info, service times, and per-page copy for
    the public site), plus upload the church logo. All content fields are
    written with is_public=true so apps/web's useSiteContent() composable
    can read them without auth via GET /site-config/public.

    Kept separate from pages/settings/index.vue, which stays focused on
    connector/infra config (email, AI moderation) — this page is purely
    the public-facing copy a non-technical admin edits.

  Why one bulk fetch instead of settings/index.vue's per-key GETs:
    This page has ~30 fields. Sequential per-key fetches (the settings page's
    pattern) would mean 30 round trips. GET /site-config already returns
    every configured row in one call, so this page fetches once and looks
    up each field from that list — still using the exact same PUT-per-key
    write path as every other admin form.

  How it connects:
    - GET  /site-config        → loads every existing key in one call
    - PUT  /site-config/{key}  → saves each changed field (is_public=true)
    - POST /site-config/logo   → uploads the logo file, returns its URL
    - apps/web app/composables/useSiteContent.ts reads these keys back via
      GET /site-config/public
-->

<script setup lang="ts">
import { reactive, ref, onMounted } from 'vue'

definePageMeta({ middleware: 'auth' })

interface FieldDef {
  key: string
  label: string
  type: 'text' | 'textarea' | 'email' | 'tel' | 'number'
  placeholder?: string
  help?: string
  isPublic?: boolean // defaults to true; set false for staff-only fields
}

interface SectionDef {
  title: string
  description: string
  fields: FieldDef[]
}

const sections: SectionDef[] = [
  {
    title: 'Church Identity',
    description: 'Shown in the navigation bar, footer, and page titles across the site.',
    fields: [
      { key: 'church_name', label: 'Church Name', type: 'text', placeholder: 'Libby Church of the Nazarene' },
    ],
  },
  {
    title: 'Location',
    description: 'Shown in the footer, About page, and Contact page.',
    fields: [
      { key: 'church_address_line1', label: 'Street Address', type: 'text', placeholder: '409 Louisiana Ave' },
      { key: 'church_city', label: 'City', type: 'text', placeholder: 'Libby' },
      { key: 'church_state', label: 'State', type: 'text', placeholder: 'MT' },
      { key: 'church_zip', label: 'ZIP Code', type: 'text', placeholder: '59923' },
    ],
  },
  {
    title: 'Contact Information',
    description: 'Shown in the footer and on the Contact page.',
    fields: [
      { key: 'church_phone', label: 'Phone Number', type: 'tel', placeholder: '(406) 293-2931' },
      { key: 'church_office_email', label: 'Office Email', type: 'email', placeholder: 'office@yourchurch.org' },
      { key: 'church_pastor_name', label: 'Pastor Name', type: 'text', placeholder: 'Pastor John Smith' },
      { key: 'church_office_hours', label: 'Office Hours', type: 'text', placeholder: 'Mon–Fri, 9am–4pm' },
    ],
  },
  {
    title: 'Service Times',
    description: 'Shown in the footer, About page, and Contact page.',
    fields: [
      { key: 'service_time_1_label', label: 'Service 1 — Label', type: 'text', placeholder: 'Sunday School' },
      { key: 'service_time_1_time', label: 'Service 1 — Time', type: 'text', placeholder: '9:30 AM' },
      { key: 'service_time_2_label', label: 'Service 2 — Label', type: 'text', placeholder: 'Morning Worship' },
      { key: 'service_time_2_time', label: 'Service 2 — Time', type: 'text', placeholder: '10:45 AM' },
      { key: 'service_time_3_label', label: 'Service 3 — Label', type: 'text', placeholder: 'Wednesday Prayer' },
      { key: 'service_time_3_time', label: 'Service 3 — Time', type: 'text', placeholder: '6:30 PM' },
    ],
  },
  {
    title: 'Home Page',
    description: 'Hero copy and the "New Here?" call-to-action.',
    fields: [
      { key: 'home_tagline', label: 'Hero Heading', type: 'text', placeholder: 'A Place to Know God and Be Known' },
      { key: 'home_welcome_message', label: 'Hero Subtext', type: 'textarea' },
      { key: 'home_new_here_heading', label: '"New Here?" Heading', type: 'text', placeholder: 'New Here? We’d Love to Meet You.' },
      { key: 'home_new_here_tagline', label: '"New Here?" Tagline', type: 'textarea' },
      { key: 'home_scripture_ref', label: 'Scripture Reference', type: 'text', placeholder: 'Matthew 22:37–39' },
      { key: 'home_scripture_text', label: 'Scripture Text', type: 'textarea' },
    ],
  },
  {
    title: 'About Page',
    description: 'Tagline, mission statement, and beliefs.',
    fields: [
      { key: 'about_tagline', label: 'Tagline', type: 'textarea' },
      { key: 'about_mission_statement', label: 'Mission Statement', type: 'textarea' },
      { key: 'about_what_we_believe', label: 'What We Believe', type: 'textarea' },
      { key: 'about_scripture_ref', label: 'Scripture Reference', type: 'text', placeholder: 'Micah 6:8' },
      { key: 'about_scripture_text', label: 'Scripture Text', type: 'textarea' },
    ],
  },
  {
    title: 'Sermons Page',
    description: 'Tagline and how many recent sermons to display.',
    fields: [
      { key: 'sermons_tagline', label: 'Tagline', type: 'textarea' },
      { key: 'sermons_display_count', label: 'Sermons to Display', type: 'number', placeholder: '6' },
    ],
  },
  {
    title: 'Giving Page',
    description: 'Header and statement shown on the Give page.',
    fields: [
      { key: 'giving_header', label: 'Header', type: 'text', placeholder: 'Give' },
      { key: 'giving_tagline', label: 'Statement', type: 'textarea' },
    ],
  },
  {
    title: 'Sermon Feed (Logos)',
    description: 'Stored for future use — sync is not yet automated.',
    fields: [
      { key: 'logos_feed_url', label: 'Logos Feed URL', type: 'text', placeholder: 'https://...', isPublic: false },
    ],
  },
]

const values = reactive<Record<string, string>>({})
for (const section of sections) {
  for (const field of section.fields) values[field.key] = ''
}

const logoUrl        = ref('')
const logoUploading  = ref(false)
const logoUploadError = ref('')

const loading    = ref(true)
const saving     = ref(false)
const saved      = ref(false)
const saveError  = ref('')

onMounted(async () => {
  try {
    const rows = await $fetch<Array<{ key: string; value: string | null }>>('/site-config')
    const byKey = new Map(rows.map(row => [row.key, row.value ?? '']))
    for (const key of Object.keys(values)) {
      if (byKey.has(key)) values[key] = byKey.get(key) as string
    }
    logoUrl.value = byKey.get('church_logo_url') ?? ''
  } catch {
    // No config saved yet — fields stay at their defaults (empty).
  } finally {
    loading.value = false
  }
})

async function handleLogoChange(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return

  logoUploading.value  = true
  logoUploadError.value = ''
  try {
    const form = new FormData()
    form.append('file', file)
    const result = await $fetch<{ url: string }>('/site-config/logo', {
      method: 'POST',
      body:   form,
    })
    logoUrl.value = result.url
  } catch {
    logoUploadError.value = 'Failed to upload logo. Please try a different file.'
  } finally {
    logoUploading.value = false
  }
}

function fieldIsPublic(field: FieldDef): boolean {
  return field.isPublic ?? true
}

async function handleSave() {
  saving.value    = true
  saved.value     = false
  saveError.value = ''
  try {
    const writes = sections.flatMap(section =>
      section.fields.map(field =>
        $fetch(`/site-config/${field.key}`, {
          method: 'PUT',
          body:   { value: values[field.key], is_public: fieldIsPublic(field) },
        }),
      ),
    )
    await Promise.all(writes)
    saved.value = true
  } catch {
    saveError.value = 'Failed to save site content. Please try again.'
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div>
    <div class="mb-6">
      <h1
        style="font-family: var(--font-display)"
        class="text-2xl font-bold text-charcoal-900 dark:text-stone-50"
      >
        Site Content
      </h1>
      <p
        style="font-family: var(--font-ui)"
        class="text-sm text-charcoal-900/50 dark:text-stone-400 mt-1"
      >
        Church identity, contact information, and page copy shown on the public site.
      </p>
    </div>

    <form data-testid="content-form" @submit.prevent="handleSave">
      <!-- Logo -->
      <div class="co-card mb-6" data-testid="logo-section">
        <h2
          style="font-family: var(--font-display)"
          class="text-lg font-semibold text-charcoal-900 dark:text-stone-50 mb-1"
        >
          Church Logo
        </h2>
        <p
          style="font-family: var(--font-ui)"
          class="text-sm text-charcoal-900/50 dark:text-stone-400 mb-4"
        >
          SVG, PNG, JPG, or GIF, up to 2MB. Shown next to the church name in the
          navigation bar. If no logo is uploaded, the church name is shown as text.
        </p>
        <div class="flex items-center gap-4">
          <img
            v-if="logoUrl"
            :src="logoUrl"
            alt="Current church logo"
            data-testid="logo-preview"
            class="h-12 w-auto max-w-[200px] object-contain bg-stone-100 dark:bg-charcoal-800 rounded p-1"
          >
          <input
            type="file"
            accept=".svg,.png,.jpg,.jpeg,.gif,image/svg+xml,image/png,image/jpeg,image/gif"
            data-testid="logo-file-input"
            :disabled="logoUploading"
            class="text-sm"
            style="font-family: var(--font-ui)"
            @change="handleLogoChange"
          >
          <span v-if="logoUploading" class="text-sm text-charcoal-900/50 dark:text-stone-400">Uploading…</span>
        </div>
        <p
          v-show="logoUploadError"
          class="text-sm text-red-600 dark:text-red-400 mt-2"
          data-testid="logo-upload-error"
        >
          {{ logoUploadError }}
        </p>
      </div>

      <!-- Data-driven sections -->
      <div
        v-for="section in sections"
        :key="section.title"
        class="co-card mb-6"
        :data-testid="`section-${section.title}`"
      >
        <h2
          style="font-family: var(--font-display)"
          class="text-lg font-semibold text-charcoal-900 dark:text-stone-50 mb-1"
        >
          {{ section.title }}
        </h2>
        <p
          style="font-family: var(--font-ui)"
          class="text-sm text-charcoal-900/50 dark:text-stone-400 mb-5"
        >
          {{ section.description }}
        </p>

        <div class="flex flex-col gap-4 max-w-xl">
          <div v-for="field in section.fields" :key="field.key" class="flex flex-col gap-1">
            <label :for="field.key" class="form-label" style="font-family: var(--font-ui)">
              {{ field.label }}
            </label>
            <textarea
              v-if="field.type === 'textarea'"
              :id="field.key"
              v-model="values[field.key]"
              :name="field.key"
              rows="3"
              class="form-input"
              style="font-family: var(--font-ui)"
              :placeholder="field.placeholder"
            />
            <input
              v-else
              :id="field.key"
              v-model="values[field.key]"
              :name="field.key"
              :type="field.type"
              class="form-input"
              style="font-family: var(--font-ui)"
              :placeholder="field.placeholder"
            >
          </div>
        </div>
      </div>

      <!-- Feedback + save -->
      <p
        v-show="saved"
        class="text-sm text-forest-600 dark:text-forest-300 mb-3"
        style="font-family: var(--font-ui)"
        data-testid="content-saved"
      >
        Site content saved successfully.
      </p>
      <p
        v-show="saveError"
        class="text-sm text-red-600 dark:text-red-400 mb-3"
        style="font-family: var(--font-ui)"
        data-testid="content-error"
      >
        {{ saveError }}
      </p>

      <button
        type="submit"
        class="btn-primary !py-1.5 !px-6 text-sm"
        style="font-family: var(--font-ui)"
        :disabled="saving || loading"
        data-testid="content-save-btn"
      >
        {{ saving ? 'Saving…' : 'Save Site Content' }}
      </button>
    </form>
  </div>
</template>
