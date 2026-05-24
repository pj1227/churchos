<!--
  packages/ui/src/components/CoSection.vue — Full-width page section with vertical rhythm.

  What it does:
    Wraps a page section in a <section> (or custom tag) with the co-section
    padding-block applied for consistent vertical spacing across pages.

  Why it exists at this layer:
    Consistent vertical rhythm between page sections (hero, sermons, events,
    about) needs one shared class rather than per-page Tailwind stacks.

  How it connects:
    Uses co-section class from packages/config/src/components.css.
    Exported from packages/ui/src/index.ts.
-->

<script setup lang="ts">
withDefaults(defineProps<{
  tag?: string
}>(), {
  tag: 'section',
})
</script>

<template>
  <component :is="tag" class="co-section">
    <slot />
  </component>
</template>
