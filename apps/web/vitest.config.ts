/**
 * vitest.config.ts — apps/web test runner configuration
 *
 * What it does:
 *   Configures vitest with Vue SFC support and happy-dom for DOM APIs.
 *   Sets up a global stub file so Nuxt auto-imports (useSeoMeta, useHead,
 *   useColorMode, etc.) are available when running tests outside Nuxt.
 *
 * Why it exists at this layer:
 *   apps/web pages use Nuxt composables that don't exist in a bare Vite/
 *   vitest environment. The setupFiles shim makes them no-ops so component
 *   rendering under test doesn't crash.
 *
 * How it connects:
 *   - tests/setup.ts: global stubs for Nuxt auto-imports
 *   - packages/ui components are resolved via pnpm workspace symlinks
 */
import { defineConfig } from 'vitest/config'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  test: {
    environment: 'happy-dom',
    globals: true,
    setupFiles: ['./tests/setup.ts'],
  },
})
