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

useSeoMeta({
  title: 'About — Libby Church of the Nazarene',
  description: 'Learn about Libby Church of the Nazarene — our mission, history, beliefs, and service times.',
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
        A community of believers in Libby, Montana — loving God and loving
        our neighbors since 1910.
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
          style="font-family: var(--font-body)"
          class="text-charcoal-900/80 dark:text-stone-200 text-lg leading-relaxed mb-4"
        >
          We exist to make Christlike disciples in the nations — beginning right
          here in Libby, Montana. That means gathering together in worship,
          growing in the knowledge of God's Word, and going into our community
          with the love and hope of Jesus.
        </p>
        <p
          style="font-family: var(--font-body)"
          class="text-charcoal-900/80 dark:text-stone-200 text-lg leading-relaxed"
        >
          As part of the Church of the Nazarene, we stand in the Wesleyan-
          Holiness tradition — believing that God's grace is available to all,
          that real transformation is possible, and that love is the mark of
          the Kingdom.
        </p>
      </div>
    </CoContainer>
  </CoSection>

  <!-- Scripture callout -->
  <CoSection class="bg-stone-100 dark:bg-charcoal-800">
    <CoContainer class="max-w-3xl">
      <div data-testid="scripture">
        <CoScriptureCallout reference="Micah 6:8">
          He has shown you, O mortal, what is good. And what does the LORD require
          of you? To act justly and to love mercy and to walk humbly with your God.
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
            Sunday School — 9:30 AM<br>
            Morning Worship — 10:45 AM
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
            Prayer &amp; Bible Study — 6:30 PM
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
          409 Louisiana Ave, Libby, MT 59923<br>
          <a href="tel:+14062932931" class="text-forest-500 hover:text-forest-600 transition-colors">
            (406) 293-2931
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
        style="font-family: var(--font-body)"
        class="text-charcoal-900/80 dark:text-stone-200 leading-relaxed mb-4"
      >
        We believe in one God — Father, Son, and Holy Spirit. We believe the
        Bible is the inspired Word of God, the sufficient rule of faith and
        practice. We believe that all people are fallen and in need of God's
        grace, and that through Jesus Christ's atoning death and resurrection,
        salvation is freely offered to all who believe.
      </p>
      <p
        style="font-family: var(--font-body)"
        class="text-charcoal-900/80 dark:text-stone-200 leading-relaxed"
      >
        We believe the Holy Spirit sanctifies believers — setting them apart and
        empowering them to love God and neighbor fully. We look forward to the
        return of Christ and the resurrection of the dead.
      </p>
    </CoContainer>
  </CoSection>
</template>
