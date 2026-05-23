/**
 * packages/ui/src/index.ts — Shared Vue component library barrel export.
 *
 * What it does:
 *   Re-exports every component so consumers can import from '@churchos/ui'
 *   rather than deep paths.
 *
 * Why it exists at this layer:
 *   A single import surface keeps app-level imports clean and lets us move
 *   files internally without breaking consumers.
 *
 * How it connects:
 *   apps/web and apps/admin import from this entry point.
 *   packages/ui/package.json "exports": { ".": "./src/index.ts" }
 */

export { default as CoButton }           from './components/CoButton.vue'
export { default as CoCard }             from './components/CoCard.vue'
export { default as CoCardFeatured }     from './components/CoCardFeatured.vue'
export { default as CoBadge }            from './components/CoBadge.vue'
export { default as CoFormInput }        from './components/CoFormInput.vue'
export { default as CoScriptureCallout } from './components/CoScriptureCallout.vue'
export { default as CoContainer }        from './components/CoContainer.vue'
export { default as CoSection }          from './components/CoSection.vue'
