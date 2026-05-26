/**
 * tests/pages/HomePage.test.ts — TDD anchor for the homepage
 *
 * What it does:
 *   Verifies the homepage renders a hero section, a scripture callout,
 *   a latest sermon teaser, and a plan-your-visit CTA.
 *
 * Why it exists at this layer:
 *   The homepage is the primary entry point for visitors. These tests lock
 *   in the required structural sections before any implementation exists.
 *
 * How it connects:
 *   Component under test: app/pages/index.vue
 *   Uses @churchos/ui components which are resolved via pnpm workspace.
 */
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import HomePage from '../../app/pages/index.vue'

const stubs = {
  NuxtLink: {
    template: '<a :href="to"><slot /></a>',
    props: ['to'],
  },
}

describe('HomePage', () => {
  it('renders a hero section', () => {
    const wrapper = mount(HomePage, { global: { stubs } })
    expect(wrapper.find('[data-testid="hero"]').exists()).toBe(true)
  })

  it('hero contains a primary heading', () => {
    const wrapper = mount(HomePage, { global: { stubs } })
    const heading = wrapper.find('h1')
    expect(heading.exists()).toBe(true)
    expect(heading.text().length).toBeGreaterThan(0)
  })

  it('hero has a plan-your-visit or join-us CTA button', () => {
    const wrapper = mount(HomePage, { global: { stubs } })
    expect(wrapper.find('[data-testid="hero-cta"]').exists()).toBe(true)
  })

  it('renders a scripture callout', () => {
    const wrapper = mount(HomePage, { global: { stubs } })
    expect(wrapper.find('[data-testid="scripture"]').exists()).toBe(true)
  })

  it('renders a latest sermon section', () => {
    const wrapper = mount(HomePage, { global: { stubs } })
    expect(wrapper.find('[data-testid="latest-sermon"]').exists()).toBe(true)
  })

  it('latest sermon section has a heading', () => {
    const wrapper = mount(HomePage, { global: { stubs } })
    const section = wrapper.find('[data-testid="latest-sermon"]')
    const heading = section.find('h2, h3')
    expect(heading.exists()).toBe(true)
  })
})
