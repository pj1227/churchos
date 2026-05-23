<!--
  packages/ui/src/components/CoFormInput.vue — Labeled text input with v-model support.

  What it does:
    Renders a label + input pair wired for v-model. Supports all standard
    input types, placeholder, disabled, and auto-associates the label via id.

  Why it exists at this layer:
    Contact forms, prayer submissions, giving fields, and auth forms all need
    the same focused ring / dark mode behavior. One source of truth prevents
    regressions across apps.

  How it connects:
    Uses form-label and form-input classes from packages/config/src/components.css.
    Exported from packages/ui/src/index.ts.
-->

<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(defineProps<{
  modelValue?: string
  label?:      string
  id?:         string
  type?:       string
  placeholder?: string
  disabled?:   boolean
}>(), {
  modelValue: '',
  type:       'text',
  disabled:   false,
})

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
}>()

// Auto-generate an id if label is provided but id is not
const inputId = computed(() => props.id ?? (props.label ? `input-${props.label.toLowerCase().replace(/\s+/g, '-')}` : undefined))
</script>

<template>
  <div>
    <label v-if="label" :for="inputId" class="form-label">
      {{ label }}
    </label>
    <input
      :id="inputId"
      class="form-input"
      :type="type"
      :placeholder="placeholder"
      :disabled="disabled"
      :value="modelValue"
      @input="emit('update:modelValue', ($event.target as HTMLInputElement).value)"
    />
  </div>
</template>
