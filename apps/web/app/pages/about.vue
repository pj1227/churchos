<!--
  app/pages/about.vue — About page (route: /about)

  What it does:
    Communicates the church's identity, mission, history, and service times to
    visitors. Contains a scripture callout, a mission statement block, a
    service times section, and a staff placeholder.

  Why it exists at this layer:
    The About page is often the second page a first-time visitor opens after
    the homepage. Static generation means it loads instantly with no server hop.

  How it connects:
    - Rendered inside app/layouts/default.vue
    - Uses @churchos/ui for consistent component styling
-->

<script setup lang="ts">
import {
  CoScriptureCallout,
  CoContainer,
  CoSection,
} from '@churchos/ui'
import { useSiteContent } from '../composables/useSiteContent'

const content = useSiteContent()

useSeoMeta({
  title: () => `About — ${content.value.church_name}`,
  description: () => `Learn about ${content.value.church_name} — our mission, history, beliefs, and service times.`,
})
</script>

<template>
  <!-- Page header -->
  <CoSection class="bg-forest-600 dark:bg-charcoal-900 py-16">
    <CoContainer>
      <h1
        style="font-family: var(--font-display)"
        class="text-4xl md:text-5xl font-bold text-white mb-3"
      >
        About Us
      </h1>
      <p
        style="font-family: var(--font-body)"
        class="text-white/70 text-lg max-w-xl"
      >
        {{ content.about_tagline }}
      </p>
    </CoContainer>
  </CoSection>

  <!-- Mission -->
  <CoSection>
    <CoContainer class="max-w-3xl">
      <div data-testid="mission">
        <h2
          style="font-family: var(--font-display)"
          class="text-2xl md:text-3xl font-semibold text-charcoal-900 dark:text-stone-50 mb-6"
        >
          Our Mission
        </h2>
        <p
          v-for="(paragraph, i) in content.about_mission_statement.split('\n\n')"
          :key="i"
          style="font-family: var(--font-body)"
          class="text-charcoal-900/80 dark:text-stone-200 text-lg leading-relaxed mb-4 last:mb-0"
        >
          {{ paragraph }}
        </p>
      </div>
    </CoContainer>
  </CoSection>

  <!-- Scripture callout -->
  <CoSection class="bg-stone-100 dark:bg-charcoal-800">
    <CoContainer class="max-w-3xl">
      <div data-testid="scripture">
        <CoScriptureCallout :reference="content.about_scripture_ref">
          {{ content.about_scripture_text }}
        </CoScriptureCallout>
      </div>
    </CoContainer>
  </CoSection>

  <!-- Service times -->
  <CoSection>
    <CoContainer class="max-w-3xl">
      <h2
        style="font-family: var(--font-display)"
        class="text-2xl md:text-3xl font-semibold text-charcoal-900 dark:text-stone-50 mb-6"
      >
        Join Us
      </h2>

      <div data-testid="service-times" class="grid grid-cols-1 sm:grid-cols-2 gap-6">
        <div class="co-card">
          <p
            style="font-family: var(--font-display)"
            class="text-lg font-semibold text-charcoal-900 dark:text-stone-50 mb-1"
          >
            Sunday Morning
          </p>
          <p style="font-family: var(--font-ui)" class="text-charcoal-900/70 dark:text-stone-300 text-sm">
            {{ content.service_time_1_label }} — {{ content.service_time_1_time }}<br>
            {{ content.service_time_2_label }} — {{ content.service_time_2_time }}
          </p>
        </div>

        <div class="co-card">
          <p
            style="font-family: var(--font-display)"
            class="text-lg font-semibold text-charcoal-900 dark:text-stone-50 mb-1"
          >
            Wednesday Evening
          </p>
          <p style="font-family: var(--font-ui)" class="text-charcoal-900/70 dark:text-stone-300 text-sm">
            {{ content.service_time_3_label }} — {{ content.service_time_3_time }}
          </p>
        </div>
      </div>

      <div class="mt-6 co-card">
        <p
          style="font-family: var(--font-display)"
          class="text-lg font-semibold text-charcoal-900 dark:text-stone-50 mb-2"
        >
          Find Us
        </p>
        <address
          style="font-family: var(--font-ui)"
          class="not-italic text-charcoal-900/70 dark:text-stone-300 text-sm leading-relaxed"
        >
          {{ content.church_address_line1 }}, {{ content.church_city }}, {{ content.church_state }} {{ content.church_zip }}<br>
          <a :href="`tel:+1${content.church_phone.replace(/\D/g, '')}`" class="text-forest-500 hover:text-forest-600 transition-colors">
            {{ content.church_phone }}
          </a>
        </address>
      </div>
    </CoContainer>
  </CoSection>

  <!-- Beliefs summary -->
  <CoSection class="bg-stone-100 dark:bg-charcoal-800">
    <CoContainer class="max-w-3xl">
      <h2
        style="font-family: var(--font-display)"
        class="text-2xl md:text-3xl font-semibold text-charcoal-900 dark:text-stone-50 mb-6"
      >
        What We Believe
      </h2>
      <p
        v-for="(paragraph, i) in content.about_what_we_believe.split('\n\n')"
        :key="i"
        style="font-family: var(--font-body)"
        class="text-charcoal-900/80 dark:text-stone-200 leading-relaxed mb-4 last:mb-0"
      >
        {{ paragraph }}
      </p>
    </CoContainer>
  </CoSection>
</template>
