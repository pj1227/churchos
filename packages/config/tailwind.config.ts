/**
 * packages/config/tailwind.config.ts — ChurchOS design token config.
 *
 * What it does:
 *   Defines all brand colors, font families, and custom utilities.
 *   Both apps/web and apps/admin extend this config so tokens stay in sync.
 *
 * Why it exists at this layer:
 *   Centralizing tokens here means a brand update touches one file, not two.
 *
 * How it connects:
 *   apps/web/nuxt.config.ts and apps/admin/nuxt.config.ts will extend this
 *   via the @churchos/config workspace package in Phase 1.
 *
 * Phase 0: Stub with color + font tokens. Full utility classes added in Phase 1.
 */
import type { Config } from 'tailwindcss'

const config: Config = {
  darkMode: 'class',
  content: [],
  theme: {
    extend: {
      colors: {
        forest: {
          50:  '#edf5f0',
          100: '#d0e8da',
          200: '#a3d0b6',
          300: '#72b890',
          400: '#4a9068',
          500: '#2d6a4f', // primary brand
          600: '#23553f', // hover
          700: '#1a3f2f',
          800: '#112a1f',
          900: '#08150f',
        },
        kootenai: {
          50:  '#eaf4f6',
          100: '#cce6ea',
          200: '#99cdd5',
          300: '#66b4c0',
          400: '#4d9bac',
          500: '#3a7d8c', // secondary
          600: '#2e6470',
          700: '#224b54',
          800: '#163238',
          900: '#0b191c',
        },
        gold: {
          50:  '#fdf6e8',
          100: '#f9e8c1',
          200: '#f3d183',
          300: '#e8b94a',
          400: '#d9a330',
          500: '#c9962b', // accent
          600: '#a37822',
          700: '#7a5a19',
          800: '#523c11',
          900: '#291e08',
        },
        charcoal: {
          700: '#1a2426',
          800: '#101819',
          900: '#0a1012', // dark surface
        },
        stone: {
          50:  '#faf8f5', // light bg
          100: '#f0ede8',
          200: '#e0dbd2',
        },
      },
      fontFamily: {
        display: ['Cinzel', 'serif'],   // h1, h2 — brand display
        body:    ['Lora', 'serif'],     // body copy, scripture
        ui:      ['DM Sans', 'sans-serif'], // nav, buttons, labels
      },
    },
  },
  plugins: [],
}

export default config
