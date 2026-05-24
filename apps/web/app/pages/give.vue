<!--
  app/pages/give.vue — Placeholder for the giving module (Phase 7).

  What it does:
    Renders a "coming soon" page at /give so the static prerenderer
    doesn't 404 when it crawls NuxtLinks pointing here.

  Why it exists at this layer:
    Phase 2 nav and pages link to /give. Static generation fails hard
    on any linked route that returns 404. This stub keeps the build
    green until the Stripe giving module is wired up in Phase 7.

  How it connects:
    Will be replaced entirely by apps/web/app/pages/give/ (directory)
    with checkout flow in Phase 7.
-->
<script setup lang="ts">
useSeoMeta({
  title: 'Give — Libby Church of the Nazarene',
  description: 'Support the ministry of Libby Church of the Nazarene.',
})
</script>

<template>
  <CoSection>
    <CoContainer>
      <div class="py-24 text-center">
        <h1 class="font-cinzel text-4xl font-bold text-charcoal-900 dark:text-stone-50 mb-6">
          Give
        </h1>
        <p class="text-lg text-charcoal-600 dark:text-stone-300 mb-8 max-w-xl mx-auto">
          Online giving is coming soon. In the meantime, you can give in person
          during any Sunday service, or mail a check to the church office.
        </p>
        <NuxtLink to="/contact" class="btn-primary">Contact Us</NuxtLink>
      </div>
    </CoContainer>
  </CoSection>
</template>
