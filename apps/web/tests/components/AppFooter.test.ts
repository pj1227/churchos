/**
 * tests/components/AppFooter.test.ts — TDD anchor for AppFooter
 *
 * What it does:
 *   Verifies the site footer renders the church name, the current version
 *   string, and a copyright notice.
 *
 * Why it exists at this layer:
 *   The project spec requires the version to be visible in the site footer.
 *   Testing it here ensures that requirement is enforced automatically.
 *
 * How it connects:
 *   Component under test: app/components/AppFooter.vue
 */
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import AppFooter from '../../app/components/AppFooter.vue'

const stubs = {
  NuxtLink: {
    template: '<a :href="to"><slot /></a>',
    props: ['to'],
  },
}

describe('AppFooter', () => {
  it('renders inside a <footer> element', () => {
    const wrapper = mount(AppFooter, { global: { stubs } })
    expect(wrapper.find('footer').exists()).toBe(true)
  })

  it('shows the church name', () => {
    const wrapper = mount(AppFooter, { global: { stubs } })
    expect(wrapper.text()).toContain('Libby Church')
  })

  it('shows the version string', () => {
    const wrapper = mount(AppFooter, { global: { stubs } })
    expect(wrapper.text()).toContain('0.1.0')
  })

  it('shows a copyright notice', () => {
    const wrapper = mount(AppFooter, { global: { stubs } })
    expect(wrapper.text()).toMatch(/©|\(c\)|copyright/i)
  })
})
