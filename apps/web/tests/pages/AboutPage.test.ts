/**
 * tests/pages/AboutPage.test.ts — TDD anchor for the About page
 *
 * What it does:
 *   Verifies the About page renders a page heading, a mission statement
 *   section, and a scripture callout.
 *
 * Why it exists at this layer:
 *   The About page communicates the church's identity to visitors. These
 *   tests ensure the key content sections exist before implementation.
 *
 * How it connects:
 *   Component under test: app/pages/about.vue
 */
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import AboutPage from '../../app/pages/about.vue'

const stubs = {
  NuxtLink: {
    template: '<a :href="to"><slot /></a>',
    props: ['to'],
  },
}

describe('AboutPage', () => {
  it('renders a page heading containing "About"', () => {
    const wrapper = mount(AboutPage, { global: { stubs } })
    const heading = wrapper.find('h1')
    expect(heading.exists()).toBe(true)
    expect(heading.text()).toMatch(/about/i)
  })

  it('renders a mission statement section', () => {
    const wrapper = mount(AboutPage, { global: { stubs } })
    expect(wrapper.find('[data-testid="mission"]').exists()).toBe(true)
  })

  it('mission section has body text', () => {
    const wrapper = mount(AboutPage, { global: { stubs } })
    const mission = wrapper.find('[data-testid="mission"]')
    expect(mission.text().length).toBeGreaterThan(20)
  })

  it('renders a scripture callout', () => {
    const wrapper = mount(AboutPage, { global: { stubs } })
    expect(wrapper.find('[data-testid="scripture"]').exists()).toBe(true)
  })

  it('renders service times section', () => {
    const wrapper = mount(AboutPage, { global: { stubs } })
    expect(wrapper.find('[data-testid="service-times"]').exists()).toBe(true)
  })
})
