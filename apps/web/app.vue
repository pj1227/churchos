<!--
  app.vue — Application shell for apps/web

  What it does:
    Minimal shell that wires Nuxt's layout system to the page router.
    NuxtLayout resolves to app/layouts/default.vue (which renders AppNav +
    AppFooter) unless a page declares a different layout via definePageMeta.

  Why it exists at this layer:
    Nuxt 4 requires app.vue as the entry point. Keeping it minimal pushes
    structural concerns (nav, footer, dark-mode class) into the layout.

  How it connects:
    - app/layouts/default.vue: provides the page chrome
    - NuxtPage: renders the matched route component from app/pages/
-->

<template>
  <NuxtLayout>
    <NuxtRouteAnnouncer />
    <NuxtPage />
  </NuxtLayout>
</template>
