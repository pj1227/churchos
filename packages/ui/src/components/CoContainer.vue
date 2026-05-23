<!--
  packages/ui/src/components/CoContainer.vue — Max-width responsive page container.

  What it does:
    Wraps content in a centered 72rem max-width container with responsive
    horizontal padding (1.5rem → 2rem → 3rem across breakpoints).

  Why it exists at this layer:
    Every page section uses the same max-width constraint. A shared component
    avoids copy-paste and makes global layout changes a one-line edit.

  How it connects:
    Uses co-container class from packages/config/src/components.css.
    Exported from packages/ui/src/index.ts.
-->

<script setup lang="ts">
withDefaults(defineProps<{
  tag?: string
}>(), {
  tag: 'div',
})
</script>

<template>
  <component :is="tag" class="co-container">
    <slot />
  </component>
</template>
