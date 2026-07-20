<!--
  packages/ui/src/components/CoCardFeatured.vue — Featured / highlighted card.

  What it does:
    Like CoCard but with a forest-500 top accent border and elevated shadow.
    Used for promoted content: featured sermon, next event, announcements.

  Why it exists at this layer:
    Visually distinguishes one item from a list without requiring ad-hoc styles
    in each page component.

  How it connects:
    Uses co-card-featured class from packages/config/src/components.css.
    Exported from packages/ui/src/index.ts.
-->

<script setup lang="ts">
defineProps<{
  title?: string
}>()
</script>

<template>
  <div class="co-card-featured">
    <p v-if="title" class="mb-3 font-semibold text-lg leading-snug text-charcoal-900 dark:text-stone-50" style="font-family: var(--font-ui)">
      {{ title }}
    </p>
    <slot />
  </div>
</template>
