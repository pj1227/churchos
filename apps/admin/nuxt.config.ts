/**
 * nuxt.config.ts — Admin dashboard (apps/admin)
 *
 * What it does:
 *   Configures the Nuxt 4 app for the staff admin dashboard. Runs as a
 *   server-side rendered app (not statically generated) so route guards
 *   and JWT checks can happen server-side.
 *
 * Why it exists at this layer:
 *   Separate from apps/web because the admin app has different build
 *   targets, auth requirements, and deployment config.
 *
 * How it connects:
 *   - Extends @churchos/config for shared Tailwind tokens
 *   - @nuxtjs/color-mode enables dark mode via class strategy
 */
export default defineNuxtConfig({
  compatibilityDate: '2024-11-01',

  future: {
    compatibilityVersion: 4,
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
