/**
 * tests/pages/PrayerPage.test.ts — TDD tests for the public prayer form
 *
 * What it does:
 *   Verifies the prayer submission page renders the correct form fields,
 *   handles the submission lifecycle (idle → loading → success/error),
 *   and respects the anonymous toggle.
 *
 * Why it exists at this layer:
 *   The prayer form is the primary public-facing interaction point for Phase 5.
 *   Tests lock in the required fields and UX states before implementation.
 *
 * How it connects:
 *   Component under test: app/pages/prayer.vue
 *   API call: POST {apiBase}/prayer-requests (stubbed via vi.stubGlobal('$fetch'))
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import PrayerPage from '../../app/pages/prayer.vue'

const stubs = {
  NuxtLink: { template: '<a :href="to"><slot /></a>', props: ['to'] },
  CoFormInput: {
    template: '<div><label :for="id">{{ label }}</label><input :id="id" :name="id" :type="type || \'text\'" v-bind="$attrs" /></div>',
    props: ['id', 'label', 'type', 'modelValue'],
    inheritAttrs: false,
  },
  CoButton: { template: '<button type="submit"><slot /></button>' },
  CoContainer: { template: '<div><slot /></div>' },
  CoSection: { template: '<section><slot /></section>' },
}

beforeEach(() => {
  vi.stubGlobal('$fetch', vi.fn().mockResolvedValue({ id: 'prayer-001', status: 'approved' }))
})

describe('PrayerPage', () => {
  it('renders a heading containing "Prayer"', () => {
    const wrapper = mount(PrayerPage, { global: { stubs } })
    const heading = wrapper.find('h1')
    expect(heading.exists()).toBe(true)
    expect(heading.text()).toMatch(/prayer/i)
  })

  it('renders a form', () => {
    const wrapper = mount(PrayerPage, { global: { stubs } })
    expect(wrapper.find('form').exists()).toBe(true)
  })

  it('form has a prayer request textarea', () => {
    const wrapper = mount(PrayerPage, { global: { stubs } })
    const textarea = wrapper.find('textarea[id="body"], textarea[name="body"]')
    expect(textarea.exists()).toBe(true)
  })

  it('form has an optional name input', () => {
    const wrapper = mount(PrayerPage, { global: { stubs } })
    const input = wrapper.find('input[id="name"], input[name="name"]')
    expect(input.exists()).toBe(true)
  })

  it('form has an optional email input', () => {
    const wrapper = mount(PrayerPage, { global: { stubs } })
    const input = wrapper.find('input[id="email"], input[name="email"], input[type="email"]')
    expect(input.exists()).toBe(true)
  })

  it('form has an anonymous checkbox', () => {
    const wrapper = mount(PrayerPage, { global: { stubs } })
    const checkbox = wrapper.find('input[type="checkbox"]')
    expect(checkbox.exists()).toBe(true)
  })

  it('form has a submit button', () => {
    const wrapper = mount(PrayerPage, { global: { stubs } })
    const btn = wrapper.find('button[type="submit"], button')
    expect(btn.exists()).toBe(true)
  })

  it('shows success message after successful submission', async () => {
    const wrapper = mount(PrayerPage, { global: { stubs } })

    await wrapper.find('textarea').setValue('Please pray for healing.')
    await wrapper.find('form').trigger('submit')
    await wrapper.vm.$nextTick()
    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toMatch(/submitted|received|thank/i)
  })

  it('shows error message when API call fails', async () => {
    vi.stubGlobal('$fetch', vi.fn().mockRejectedValue(new Error('Network error')))
    const wrapper = mount(PrayerPage, { global: { stubs } })

    await wrapper.find('textarea').setValue('Please pray for healing.')
    await wrapper.find('form').trigger('submit')
    await wrapper.vm.$nextTick()
    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toMatch(/error|failed|wrong/i)
  })

  it('hides name field when anonymous is checked', async () => {
    // attachTo so isVisible() can read computed styles
    const div = document.createElement('div')
    document.body.appendChild(div)
    const wrapper = mount(PrayerPage, { global: { stubs }, attachTo: div })

    // Before checking — name wrapper is visible
    expect(wrapper.find('input[name="name"]').exists()).toBe(true)

    await wrapper.find('input[type="checkbox"]').setValue(true)
    await wrapper.vm.$nextTick()

    // After checking — name wrapper hidden via v-show (display: none)
    expect(wrapper.find('input[name="name"]').isVisible()).toBe(false)

    wrapper.unmount()
    div.remove()
  })
})
