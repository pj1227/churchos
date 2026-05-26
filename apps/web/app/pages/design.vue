<!--
  apps/web/app/pages/design.vue — Design system showcase page.

  What it does:
    Renders every shared component from @churchos/ui with all variants and
    color modes. Used to visually verify the design system during development.

  Why it exists at this layer:
    A living reference page catches visual regressions instantly and gives
    designers a direct URL to review the component library in-browser.

  How it connects:
    Imports all components from @churchos/ui. All styling comes from
    @churchos/config tokens via assets/css/main.css.
    Route: /design (removed from production via robots meta + route middleware in Phase 3).
-->

<script setup lang="ts">
import {
  CoButton,
  CoCard,
  CoCardFeatured,
  CoBadge,
  CoFormInput,
  CoScriptureCallout,
  CoContainer,
  CoSection,
} from '@churchos/ui'

import { useColorMode } from '#imports'
import { ref } from 'vue'

const colorMode = useColorMode()
const email = ref('')
const name  = ref('')

function toggleDark() {
  colorMode.preference = colorMode.value === 'dark' ? 'light' : 'dark'
}

useSeoMeta({ robots: 'noindex, nofollow' })
</script>

<template>
  <div :class="colorMode.value === 'dark' ? 'dark' : ''" class="min-h-screen bg-stone-50 dark:bg-charcoal-900 transition-colors">

    <!-- Header -->
    <header class="sticky top-0 z-10 bg-forest-500 text-white px-6 py-3 flex items-center justify-between shadow-md">
      <span style="font-family: var(--font-display)" class="text-lg font-semibold tracking-wide">
        ChurchOS Design System
      </span>
      <CoButton variant="ghost" class="!text-white hover:!bg-forest-600" @click="toggleDark">
        {{ colorMode.value === 'dark' ? '☀ Light' : '☾ Dark' }}
      </CoButton>
    </header>

    <CoContainer>

      <!-- ── Buttons ──────────────────────────────────────────────────────── -->
      <CoSection>
        <h2 style="font-family: var(--font-display)" class="text-2xl font-semibold text-charcoal-900 dark:text-stone-50 mb-6">
          Buttons
        </h2>
        <div class="flex flex-wrap gap-4 items-center">
          <CoButton variant="primary">Primary</CoButton>
          <CoButton variant="secondary">Secondary</CoButton>
          <CoButton variant="ghost">Ghost</CoButton>
          <CoButton variant="primary" disabled>Disabled</CoButton>
          <CoButton variant="primary" tag="a" href="#">Link Button</CoButton>
        </div>
      </CoSection>

      <!-- ── Badges ───────────────────────────────────────────────────────── -->
      <CoSection>
        <h2 style="font-family: var(--font-display)" class="text-2xl font-semibold text-charcoal-900 dark:text-stone-50 mb-6">
          Badges
        </h2>
        <div class="flex flex-wrap gap-3 items-center">
          <CoBadge color="forest">Sermon</CoBadge>
          <CoBadge color="kootenai">Event</CoBadge>
          <CoBadge color="gold">Featured</CoBadge>
        </div>
      </CoSection>

      <!-- ── Cards ────────────────────────────────────────────────────────── -->
      <CoSection>
        <h2 style="font-family: var(--font-display)" class="text-2xl font-semibold text-charcoal-900 dark:text-stone-50 mb-6">
          Cards
        </h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <CoCard title="Sunday Morning Service">
            <p style="font-family: var(--font-body)" class="text-charcoal-900 dark:text-stone-100 leading-relaxed">
              Join us every Sunday at 10:30am for worship, teaching from God's
              Word, and community.
            </p>
            <div class="mt-4">
              <CoBadge color="forest">Worship</CoBadge>
            </div>
          </CoCard>

          <CoCardFeatured title="This Week's Sermon">
            <p style="font-family: var(--font-body)" class="text-charcoal-900 dark:text-stone-100 leading-relaxed">
              "Walking by Faith" — Pastor explores what it means to trust God
              in uncertain times.
            </p>
            <div class="mt-4 flex gap-2">
              <CoBadge color="gold">Featured</CoBadge>
              <CoBadge color="kootenai">Series</CoBadge>
            </div>
          </CoCardFeatured>
        </div>
      </CoSection>

      <!-- ── Scripture ─────────────────────────────────────────────────────── -->
      <CoSection>
        <h2 style="font-family: var(--font-display)" class="text-2xl font-semibold text-charcoal-900 dark:text-stone-50 mb-6">
          Scripture Callout
        </h2>
        <CoScriptureCallout reference="John 3:16">
          For God so loved the world that he gave his one and only Son, that
          whoever believes in him shall not perish but have eternal life.
        </CoScriptureCallout>
      </CoSection>

      <!-- ── Form inputs ───────────────────────────────────────────────────── -->
      <CoSection>
        <h2 style="font-family: var(--font-display)" class="text-2xl font-semibold text-charcoal-900 dark:text-stone-50 mb-6">
          Form Inputs
        </h2>
        <div class="max-w-md flex flex-col gap-4">
          <CoFormInput v-model="name" label="Full name" id="name" placeholder="Jane Smith" />
          <CoFormInput v-model="email" label="Email address" id="email" type="email" placeholder="jane@example.com" />
          <CoFormInput label="Disabled field" disabled placeholder="Cannot edit" />
          <CoButton variant="primary" class="self-start">Submit</CoButton>
        </div>
      </CoSection>

      <!-- ── Color palette ─────────────────────────────────────────────────── -->
      <CoSection>
        <h2 style="font-family: var(--font-display)" class="text-2xl font-semibold text-charcoal-900 dark:text-stone-50 mb-6">
          Color Tokens
        </h2>
        <div class="flex flex-col gap-4">
          <div>
            <p class="text-sm font-medium mb-2" style="font-family: var(--font-ui)">Forest (primary)</p>
            <div class="flex gap-1">
              <div v-for="shade in [50,100,200,300,400,500,600,700,800,900]" :key="shade"
                class="h-10 flex-1 rounded"
                :style="`background-color: var(--color-forest-${shade})`"
                :title="`forest-${shade}`"
              />
            </div>
          </div>
          <div>
            <p class="text-sm font-medium mb-2" style="font-family: var(--font-ui)">Kootenai (secondary)</p>
            <div class="flex gap-1">
              <div v-for="shade in [50,100,200,300,400,500,600,700,800,900]" :key="shade"
                class="h-10 flex-1 rounded"
                :style="`background-color: var(--color-kootenai-${shade})`"
                :title="`kootenai-${shade}`"
              />
            </div>
          </div>
          <div>
            <p class="text-sm font-medium mb-2" style="font-family: var(--font-ui)">Gold (accent)</p>
            <div class="flex gap-1">
              <div v-for="shade in [50,100,200,300,400,500,600,700,800,900]" :key="shade"
                class="h-10 flex-1 rounded"
                :style="`background-color: var(--color-gold-${shade})`"
                :title="`gold-${shade}`"
              />
            </div>
          </div>
        </div>
      </CoSection>

      <!-- ── Typography ────────────────────────────────────────────────────── -->
      <CoSection>
        <h2 style="font-family: var(--font-display)" class="text-2xl font-semibold text-charcoal-900 dark:text-stone-50 mb-6">
          Typography
        </h2>
        <div class="flex flex-col gap-4">
          <p style="font-family: var(--font-display)" class="text-4xl text-charcoal-900 dark:text-stone-50">
            Cinzel — Display / Headings
          </p>
          <p style="font-family: var(--font-body)" class="text-xl text-charcoal-900 dark:text-stone-100 leading-relaxed">
            Lora — Body copy and scripture. Graceful serifs carry the weight of the Word.
          </p>
          <p style="font-family: var(--font-ui)" class="text-base text-charcoal-900 dark:text-stone-100">
            DM Sans — UI elements: navigation, buttons, form labels, badges.
          </p>
        </div>
      </CoSection>

    </CoContainer>

    <!-- Footer -->
    <footer class="border-t border-stone-200 dark:border-charcoal-700 py-6 text-center">
      <p style="font-family: var(--font-ui)" class="text-sm text-charcoal-900 dark:text-stone-200 opacity-60">
        ChurchOS v0.1.0 "Kootenai" — Design System
      </p>
    </footer>

  </div>
</template>
