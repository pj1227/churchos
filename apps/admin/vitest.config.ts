/**
 * vitest.config.ts — apps/admin test runner configuration
 *
 * What it does:
 *   Configures vitest with Vue SFC support and happy-dom for DOM APIs.
 *   Adds the ~ alias (mirrors Nuxt's convention) so test imports like
 *   `~/stores/auth` resolve to `./app/stores/auth` without a running
 *   Nuxt instance.
 *
 * Why it exists at this layer:
 *   Nuxt auto-imports and path aliases are injected by Nuxt's Vite plugin
 *   at build time. Vitest runs without that plugin, so we replicate the
 *   minimum needed: the ~ → ./app alias and global composable stubs.
 *
 * How it connects:
 *   - tests/setup.ts: stubs useSupabaseClient, $fetch, and other Nuxt globals
 *   - app/stores/auth.ts: imported via ~/stores/auth in tests
 */
import { resolve } from 'path'
import { defineConfig } from 'vitest/config'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      // Mirror Nuxt 4's ~ alias: points to the app/ source directory
      '~': resolve(__dirname, './app'),
    },
  },
  test: {
    environment: 'happy-dom',
    globals: true,
    setupFiles: ['./tests/setup.ts'],
  },
})
