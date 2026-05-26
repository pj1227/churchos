<!--
  packages/ui/src/components/CoButton.vue — Polymorphic button / link component.

  What it does:
    Renders a styled button using the shared btn-* component classes. Supports
    three variants (primary, secondary, ghost) and can render as any HTML tag
    (e.g. <a> for navigation).

  Why it exists at this layer:
    All buttons across web and admin use identical interaction states. A single
    component ensures hover/focus/disabled styling is never duplicated.

  How it connects:
    Uses the btn-primary / btn-secondary / btn-ghost classes defined in
    packages/config/src/components.css. Exported from packages/ui/src/index.ts.
-->

<script setup lang="ts">
import { computed } from 'vue'

type Variant = 'primary' | 'secondary' | 'ghost'
type Tag     = 'button' | 'a' | 'router-link' | 'NuxtLink'

const props = withDefaults(defineProps<{
  variant?:  Variant
  tag?:      Tag
  href?:     string
  disabled?: boolean
}>(), {
  variant:  'primary',
  tag:      'button',
  disabled: false,
})

const emit = defineEmits<{
  (e: 'click', event: MouseEvent): void
}>()

const variantClass = computed(() => ({
  primary:   'btn-primary',
  secondary: 'btn-secondary',
  ghost:     'btn-ghost',
})[props.variant])

function handleClick(event: MouseEvent) {
  if (props.disabled) return
  emit('click', event)
}
</script>

<template>
  <component
    :is="tag"
    :class="variantClass"
    :disabled="tag === 'button' ? disabled : undefined"
    :href="href"
    :aria-disabled="disabled || undefined"
    v-bind="$attrs"
    @click="handleClick"
  >
    <slot />
  </component>
</template>
