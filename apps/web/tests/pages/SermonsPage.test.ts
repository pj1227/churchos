/**
 * tests/pages/SermonsPage.test.ts — TDD anchor for the sermons listing
 *
 * What it does:
 *   Verifies the sermons page renders a page heading, at least one sermon
 *   card, and that each card has a title and speaker.
 *
 * Why it exists at this layer:
 *   Sermons are the primary content offering. These tests ensure the listing
 *   structure is correct before the component is written and before real data
 *   is wired in Phase 4 (admin CRUD).
 *
 * How it connects:
 *   Component under test: app/pages/sermons/index.vue
 */
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import SermonsPage from '../../app/pages/sermons/index.vue'

const stubs = {
  NuxtLink: {
    template: '<a :href="to"><slot /></a>',
    props: ['to'],
  },
}

describe('SermonsPage', () => {
  it('renders a page heading containing "Sermon"', () => {
    const wrapper = mount(SermonsPage, { global: { stubs } })
    const heading = wrapper.find('h1')
    expect(heading.exists()).toBe(true)
    expect(heading.text()).toMatch(/sermon/i)
  })

  it('renders at least one sermon card', () => {
    const wrapper = mount(SermonsPage, { global: { stubs } })
    expect(wrapper.findAll('[data-testid="sermon-card"]').length).toBeGreaterThan(0)
  })

  it('each sermon card has a title', () => {
    const wrapper = mount(SermonsPage, { global: { stubs } })
    const cards = wrapper.findAll('[data-testid="sermon-card"]')
    for (const card of cards) {
      expect(card.find('[data-testid="sermon-title"]').exists()).toBe(true)
    }
  })

  it('each sermon card has a speaker name', () => {
    const wrapper = mount(SermonsPage, { global: { stubs } })
    const cards = wrapper.findAll('[data-testid="sermon-card"]')
    for (const card of cards) {
      expect(card.find('[data-testid="sermon-speaker"]').exists()).toBe(true)
    }
  })

  it('renders a series badge on at least one card', () => {
    const wrapper = mount(SermonsPage, { global: { stubs } })
    expect(wrapper.find('[data-testid="sermon-series"]').exists()).toBe(true)
  })
})
