/**
 * packages/ui/vitest.config.ts — Vitest configuration for the shared UI library.
 *
 * What it does:
 *   Configures Vitest to run Vue component tests using happy-dom as the
 *   simulated browser environment.
 *
 * Why it exists at this layer:
 *   packages/ui is a standalone workspace package — it needs its own test
 *   config so `pnpm turbo test` can target it independently.
 *
 * How it connects:
 *   packages/ui/package.json "test": "vitest run" invokes this config.
 */

import { defineConfig } from 'vitest/config'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  test: {
    environment: 'happy-dom',
    globals: true,
  },
})
