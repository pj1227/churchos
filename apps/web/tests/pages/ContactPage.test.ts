/**
 * tests/pages/ContactPage.test.ts — TDD anchor for the Contact page
 *
 * What it does:
 *   Verifies the Contact page renders a heading, a contact form with name,
 *   email, and message fields, a submit button, and the church address.
 *
 * Why it exists at this layer:
 *   The contact form is the visitor's primary pathway to engagement. These
 *   tests lock in required form fields and accessibility structure before
 *   any implementation exists (actual submission wired in Phase 3+).
 *
 * How it connects:
 *   Component under test: app/pages/contact.vue
 */
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import ContactPage from '../../app/pages/contact.vue'

const stubs = {
  NuxtLink: {
    template: '<a :href="to"><slot /></a>',
    props: ['to'],
  },
}

describe('ContactPage', () => {
  it('renders a page heading containing "Contact"', () => {
    const wrapper = mount(ContactPage, { global: { stubs } })
    const heading = wrapper.find('h1')
    expect(heading.exists()).toBe(true)
    expect(heading.text()).toMatch(/contact/i)
  })

  it('renders a <form> element', () => {
    const wrapper = mount(ContactPage, { global: { stubs } })
    expect(wrapper.find('form').exists()).toBe(true)
  })

  it('form has a name input', () => {
    const wrapper = mount(ContactPage, { global: { stubs } })
    const input = wrapper.find('input[id="name"], input[name="name"]')
    expect(input.exists()).toBe(true)
  })

  it('form has an email input', () => {
    const wrapper = mount(ContactPage, { global: { stubs } })
    const input = wrapper.find('input[type="email"], input[id="email"], input[name="email"]')
    expect(input.exists()).toBe(true)
  })

  it('form has a message textarea', () => {
    const wrapper = mount(ContactPage, { global: { stubs } })
    expect(wrapper.find('textarea').exists()).toBe(true)
  })

  it('form has a submit button', () => {
    const wrapper = mount(ContactPage, { global: { stubs } })
    const btn = wrapper.find('button[type="submit"], button')
    expect(btn.exists()).toBe(true)
  })

  it('renders church address information', () => {
    const wrapper = mount(ContactPage, { global: { stubs } })
    expect(wrapper.find('[data-testid="church-address"]').exists()).toBe(true)
  })
})
