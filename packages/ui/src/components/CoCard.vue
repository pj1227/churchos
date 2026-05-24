<!--
  packages/ui/src/components/CoCard.vue — Standard content card.

  What it does:
    Renders a bordered, shadowed card container with optional title. Uses the
    co-card class from the shared design system.

  Why it exists at this layer:
    Sermon cards, event cards, and info blocks all share the same visual
    container. One component, consistent spacing and hover elevation.

  How it connects:
    Uses co-card class from packages/config/src/components.css.
    Exported from packages/ui/src/index.ts.
-->

<script setup lang="ts">
defineProps<{
  title?: string
}>()
</script>

<template>
  <div class="co-card">
    <p v-if="title" class="mb-3 font-semibold text-lg leading-snug" style="font-family: var(--font-ui)">
      {{ title }}
    </p>
    <slot />
  </div>
</template>
