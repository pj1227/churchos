<!--
  packages/ui/src/components/CoScriptureCallout.vue — Gold-accented scripture quote block.

  What it does:
    Renders a blockquote with a gold left border, italic Lora font body, and
    optional scripture reference attribution below the quote.

  Why it exists at this layer:
    Scripture citations appear on the homepage, sermon pages, and potentially
    prayer and giving pages. The shared component guarantees typographic
    consistency everywhere a verse is displayed.

  How it connects:
    Uses scripture-callout class from packages/config/src/components.css.
    Exported from packages/ui/src/index.ts.
-->

<script setup lang="ts">
defineProps<{
  reference?: string
}>()
</script>

<template>
  <blockquote class="scripture-callout">
    <slot />
    <footer
      v-if="reference"
      class="mt-2 text-sm not-italic font-semibold"
      style="font-family: var(--font-ui); opacity: 0.75"
    >
      — {{ reference }}
    </footer>
  </blockquote>
</template>
