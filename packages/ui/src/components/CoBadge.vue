<!--
  packages/ui/src/components/CoBadge.vue — Pill-shaped label badge.

  What it does:
    Renders a small colored pill label in one of the three brand colors:
    forest (green), kootenai (teal), or gold. Used for categories, statuses,
    and tags on sermon cards, events, and prayer requests.

  Why it exists at this layer:
    Badges need to be consistent across all listing views. Centralizing the
    color mapping here avoids ad-hoc inline class strings.

  How it connects:
    Uses badge-forest / badge-kootenai / badge-gold classes from
    packages/config/src/components.css. Exported from packages/ui/src/index.ts.
-->

<script setup lang="ts">
import { computed } from 'vue'

type BadgeColor = 'forest' | 'kootenai' | 'gold'

const props = withDefaults(defineProps<{
  color?: BadgeColor
}>(), {
  color: 'forest',
})

const badgeClass = computed(() => ({
  forest:   'badge-forest',
  kootenai: 'badge-kootenai',
  gold:     'badge-gold',
})[props.color])
</script>

<template>
  <span :class="badgeClass">
    <slot />
  </span>
</template>
