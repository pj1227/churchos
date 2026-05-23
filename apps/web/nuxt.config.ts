/**
 * nuxt.config.ts — Public website (apps/web)
 *
 * What it does:
 *   Configures the Nuxt 4 app for the public church website. Extends the
 *   shared Tailwind design token config from packages/config.
 *
 * Why it exists at this layer:
 *   Each Nuxt app needs its own config. This one enables static generation
 *   (nuxt generate) for Cloudflare Pages deployment.
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
      title: 'Libby Church of the Nazarene',
      meta: [
        { charset: 'utf-8' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
        { name: 'description', content: 'Welcome to Libby Church of the Nazarene' },
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
