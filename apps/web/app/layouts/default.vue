<!--
  app/layouts/default.vue — Default page layout for the public website

  What it does:
    Wraps every public page with AppNav at the top, a main content slot, and
    AppFooter at the bottom. Also applies the dark/light class to the root
    element based on @nuxtjs/color-mode so Tailwind's 'dark:' utilities work
    everywhere.

  Why it exists at this layer:
    Nuxt's layout system lets every page opt into the same chrome without
    each page manually importing and rendering nav/footer. The dark mode
    class needs to live on the outermost element — the layout is the right
    place for that.

  How it connects:
    - app.vue renders <NuxtLayout> which resolves to this file by default
    - AppNav and AppFooter are in app/components/ (auto-imported by Nuxt)
    - useColorMode() is a Nuxt auto-import from @nuxtjs/color-mode
-->

<script setup lang="ts">
const colorMode = useColorMode()
</script>

<template>
  <div
    :class="colorMode.value === 'dark' ? 'dark' : ''"
    class="min-h-screen flex flex-col bg-stone-50 dark:bg-charcoal-900 transition-colors"
  >
    <AppNav />

    <main class="flex-1">
      <slot />
    </main>

    <AppFooter />
  </div>
</template>
