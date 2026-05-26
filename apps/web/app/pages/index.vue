<!--
  app/pages/index.vue — Homepage (route: /)

  What it does:
    Public homepage with a full-bleed hero section, a scripture callout,
    a latest sermon teaser, and an upcoming services strip. Static content
    for now — data will be fetched from the API in Phase 4.

  Why it exists at this layer:
    The root route is the first impression for every visitor and the primary
    SEO entry point for the church. Keeping it statically generated means
    zero server dependency for initial page load.

  How it connects:
    - Rendered inside app/layouts/default.vue (AppNav + AppFooter)
    - Uses @churchos/ui components for consistent design-system styling
    - useSeoMeta: Nuxt auto-import, sets <head> meta for the page
-->

<script setup lang="ts">
import {
  CoButton,
  CoCard,
  CoCardFeatured,
  CoBadge,
  CoScriptureCallout,
  CoContainer,
  CoSection,
} from '@churchos/ui'

useSeoMeta({
  title: 'Libby Church of the Nazarene',
  description: 'A community of faith in Libby, Montana. Join us Sunday mornings for worship and God\'s Word.',
  ogTitle: 'Libby Church of the Nazarene',
  ogDescription: 'A community of faith in Libby, Montana.',
})
</script>

<template>
  <!-- ── Hero ──────────────────────────────────────────────────────────────── -->
  <section data-testid="hero" class="relative bg-forest-600 dark:bg-charcoal-900 overflow-hidden">
    <!-- Decorative gradient overlay -->
    <div
      class="absolute inset-0 opacity-20"
      style="background: linear-gradient(135deg, var(--color-kootenai-700) 0%, var(--color-forest-900) 100%)"
      aria-hidden="true"
    />

    <CoContainer class="relative py-24 md:py-36 flex flex-col items-center text-center gap-6">
      <CoBadge color="gold" class="mb-2">Libby, Montana</CoBadge>

      <h1
        style="font-family: var(--font-display)"
        class="text-4xl md:text-6xl font-bold text-white leading-tight max-w-3xl"
      >
        A Place to Know God<br class="hidden md:block"> and Be Known
      </h1>

      <p
        style="font-family: var(--font-body)"
        class="text-white/80 text-lg md:text-xl max-w-xl leading-relaxed"
      >
        Join us every Sunday morning for worship, teaching from God's Word,
        and a community that walks alongside you.
      </p>

      <div class="flex flex-wrap gap-4 justify-center mt-2">
        <NuxtLink to="/about" data-testid="hero-cta">
          <CoButton variant="primary" class="!text-base !px-8 !py-3">
            Plan Your Visit
          </CoButton>
        </NuxtLink>
        <NuxtLink to="/sermons">
          <CoButton variant="ghost" class="!text-white !border-white/40 hover:!bg-white/10 !text-base !px-8 !py-3">
            Watch Sermons
          </CoButton>
        </NuxtLink>
      </div>

      <!-- Service times pill -->
      <div
        style="font-family: var(--font-ui)"
        class="mt-4 inline-flex items-center gap-2 bg-white/10 backdrop-blur rounded-full px-5 py-2 text-white/90 text-sm"
      >
        <span class="text-gold-400">⊙</span>
        <span>Sundays · 9:30 AM Sunday School · 10:45 AM Worship</span>
      </div>
    </CoContainer>
  </section>

  <!-- ── Scripture callout ──────────────────────────────────────────────── -->
  <CoSection data-testid="scripture" class="bg-stone-100 dark:bg-charcoal-800">
    <CoContainer class="max-w-3xl">
      <CoScriptureCallout reference="Matthew 22:37–39">
        Love the Lord your God with all your heart and with all your soul and
        with all your mind. This is the first and greatest commandment. And the
        second is like it: Love your neighbor as yourself.
      </CoScriptureCallout>
    </CoContainer>
  </CoSection>

  <!-- ── Latest sermon ─────────────────────────────────────────────────── -->
  <CoSection data-testid="latest-sermon">
    <CoContainer>
      <div class="flex items-baseline justify-between mb-8">
        <h2
          style="font-family: var(--font-display)"
          class="text-2xl md:text-3xl font-semibold text-charcoal-900 dark:text-stone-50"
        >
          Latest Sermon
        </h2>
        <NuxtLink
          to="/sermons"
          style="font-family: var(--font-ui)"
          class="text-forest-500 hover:text-forest-600 text-sm font-medium transition-colors"
        >
          All sermons →
        </NuxtLink>
      </div>

      <CoCardFeatured title="Walking by Faith in Uncertain Times">
        <div class="flex flex-wrap gap-2 mb-3">
          <CoBadge color="gold">Featured</CoBadge>
          <CoBadge color="kootenai">Faith &amp; Courage Series</CoBadge>
        </div>
        <p style="font-family: var(--font-body)" class="text-charcoal-900 dark:text-stone-100 leading-relaxed mb-4">
          What does it look like to trust God when the path ahead is unclear?
          This week we explore Hebrews 11 and the heroes of faith who stepped
          forward without seeing the end.
        </p>
        <div
          style="font-family: var(--font-ui)"
          class="text-sm text-charcoal-900/60 dark:text-stone-300/60 flex flex-wrap gap-4"
        >
          <span>Pastor John Smith</span>
          <span>·</span>
          <span>Hebrews 11:1–6</span>
          <span>·</span>
          <span>May 18, 2025</span>
        </div>
      </CoCardFeatured>
    </CoContainer>
  </CoSection>

  <!-- ── Upcoming events teaser ────────────────────────────────────────── -->
  <CoSection class="bg-stone-100 dark:bg-charcoal-800">
    <CoContainer>
      <h2
        style="font-family: var(--font-display)"
        class="text-2xl md:text-3xl font-semibold text-charcoal-900 dark:text-stone-50 mb-8"
      >
        Coming Up
      </h2>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <CoCard title="Sunday Morning Worship">
          <p style="font-family: var(--font-ui)" class="text-charcoal-900/70 dark:text-stone-300 text-sm leading-relaxed">
            Every Sunday · 10:45 AM<br>Main Sanctuary
          </p>
          <div class="mt-3">
            <CoBadge color="forest">Weekly</CoBadge>
          </div>
        </CoCard>

        <CoCard title="Wednesday Prayer Service">
          <p style="font-family: var(--font-ui)" class="text-charcoal-900/70 dark:text-stone-300 text-sm leading-relaxed">
            Every Wednesday · 6:30 PM<br>Fellowship Hall
          </p>
          <div class="mt-3">
            <CoBadge color="forest">Weekly</CoBadge>
          </div>
        </CoCard>

        <CoCard title="Men's Breakfast">
          <p style="font-family: var(--font-ui)" class="text-charcoal-900/70 dark:text-stone-300 text-sm leading-relaxed">
            First Saturday of the month · 8:00 AM<br>Fellowship Hall
          </p>
          <div class="mt-3">
            <CoBadge color="kootenai">Monthly</CoBadge>
          </div>
        </CoCard>
      </div>
    </CoContainer>
  </CoSection>

  <!-- ── Connect CTA strip ─────────────────────────────────────────────── -->
  <CoSection class="bg-forest-500 dark:bg-forest-700">
    <CoContainer class="text-center">
      <h2
        style="font-family: var(--font-display)"
        class="text-2xl md:text-3xl font-semibold text-white mb-4"
      >
        New Here? We'd Love to Meet You.
      </h2>
      <p
        style="font-family: var(--font-body)"
        class="text-white/80 max-w-xl mx-auto mb-8 leading-relaxed"
      >
        Whether you're exploring faith for the first time or looking for a
        church home in Libby, you're welcome here. Reach out — we'll be in touch.
      </p>
      <NuxtLink to="/contact">
        <CoButton variant="secondary" class="!text-base !px-8 !py-3">
          Get in Touch
        </CoButton>
      </NuxtLink>
    </CoContainer>
  </CoSection>
</template>
