/**
 * tests/components/AppNav.test.ts — TDD anchor for AppNav
 *
 * What it does:
 *   Verifies the site navigation renders the church name, all four nav links,
 *   and a "Give" call-to-action button.
 *
 * Why it exists at this layer:
 *   Navigation is the skeleton of every public page. These tests document the
 *   required links and accessible semantics before the component is written.
 *
 * How it connects:
 *   Component under test: app/components/AppNav.vue
 */
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import AppNav from '../../app/components/AppNav.vue'

const stubs = {
  NuxtLink: {
    template: '<a :href="to"><slot /></a>',
    props: ['to'],
  },
}

describe('AppNav', () => {
  it('renders inside a <nav> element', () => {
    const wrapper = mount(AppNav, { global: { stubs } })
    expect(wrapper.find('nav').exists()).toBe(true)
  })

  it('shows the church name', () => {
    const wrapper = mount(AppNav, { global: { stubs } })
    expect(wrapper.text()).toContain('Libby Church')
  })

  it('has a Home link', () => {
    const wrapper = mount(AppNav, { global: { stubs } })
    expect(wrapper.text()).toContain('Home')
  })

  it('has a Sermons link', () => {
    const wrapper = mount(AppNav, { global: { stubs } })
    expect(wrapper.text()).toContain('Sermons')
  })

  it('has an About link', () => {
    const wrapper = mount(AppNav, { global: { stubs } })
    expect(wrapper.text()).toContain('About')
  })

  it('has a Contact link', () => {
    const wrapper = mount(AppNav, { global: { stubs } })
    expect(wrapper.text()).toContain('Contact')
  })

  it('has a Give call-to-action', () => {
    const wrapper = mount(AppNav, { global: { stubs } })
    expect(wrapper.text()).toContain('Give')
  })
})
