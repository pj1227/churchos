/**
 * tests/pages/GivePage.test.ts — TDD anchor for the Give placeholder page
 *
 * What it does:
 *   Verifies the Give page renders a heading, body copy, and a link back
 *   to Contact — this page stays a placeholder until Phase 8 (Stripe).
 *
 * How it connects:
 *   Component under test: app/pages/give.vue
 *   Content: useSiteContent() (giving_header, giving_tagline)
 */
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import GivePage from '../../app/pages/give.vue'

const stubs = {
  NuxtLink: { template: '<a :href="to"><slot /></a>', props: ['to'] },
  CoSection: { template: '<section><slot /></section>' },
  CoContainer: { template: '<div><slot /></div>' },
}

describe('GivePage', () => {
  it('renders a heading', () => {
    const wrapper = mount(GivePage, { global: { stubs } })
    const heading = wrapper.find('h1')
    expect(heading.exists()).toBe(true)
    expect(heading.text().length).toBeGreaterThan(0)
  })

  it('renders body copy', () => {
    const wrapper = mount(GivePage, { global: { stubs } })
    expect(wrapper.find('p').text().length).toBeGreaterThan(0)
  })

  it('links back to Contact', () => {
    const wrapper = mount(GivePage, { global: { stubs } })
    expect(wrapper.find('a[href="/contact"]').exists()).toBe(true)
  })
})
