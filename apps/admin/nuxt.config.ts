/**
 * nuxt.config.ts — Admin dashboard (apps/admin)
 *
 * What it does:
 *   Configures the Nuxt 4 app for the staff admin dashboard. Wires up
 *   Tailwind CSS v4 via the @tailwindcss/vite plugin and loads the shared
 *   design tokens from packages/config.
 *
 * Why it exists at this layer:
 *   Separate from apps/web because the admin app has different build
 *   targets, auth requirements, and deployment config.
 *
 * How it connects:
 *   - vite.plugins: [@tailwindcss/vite] processes assets/css/main.css
 *   - assets/css/main.css imports tailwindcss + @churchos/config tokens
 *   - @nuxtjs/color-mode enables dark mode via class strategy
 */
import tailwindcss from '@tailwindcss/vite'

export default defineNuxtConfig({
  compatibilityDate: '2024-11-01',

  future: {
    compatibilityVersion: 4,
  },

  vite: {
    plugins: [tailwindcss()],
  },

  modules: [
    '@nuxtjs/color-mode',
  ],

  colorMode: {
    classSuffix: '',
    preference: 'system',
    fallback: 'light',
  },

  css: ['~/assets/css/main.css'],

  app: {
    head: {
      title: 'ChurchOS Admin',
      meta: [
        { charset: 'utf-8' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
        { name: 'robots', content: 'noindex, nofollow' },
      ],
      link: [
        {
          rel: 'preconnect',
          href: 'https://fonts.googleapis.com',
        },
        {
          rel: 'stylesheet',
          href: 'https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700&family=Lora:ital,wght@0,400;0,600;1,400&family=DM+Sans:wght@400;500;600&display=swap',
        },
      ],
    },
  },
})
