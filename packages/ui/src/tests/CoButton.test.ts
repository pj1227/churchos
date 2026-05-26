/**
 * packages/ui/src/tests/CoButton.test.ts — TDD anchor for CoButton.
 *
 * Written BEFORE CoButton.vue exists. These tests must fail first.
 * Run: pnpm --filter @churchos/ui test
 */

import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import CoButton from '../components/CoButton.vue'

describe('CoButton', () => {
  it('renders slot content', () => {
    const wrapper = mount(CoButton, { slots: { default: 'Click me' } })
    expect(wrapper.text()).toBe('Click me')
  })

  it('applies btn-primary class by default', () => {
    const wrapper = mount(CoButton)
    expect(wrapper.classes()).toContain('btn-primary')
  })

  it('applies btn-secondary class when variant="secondary"', () => {
    const wrapper = mount(CoButton, { props: { variant: 'secondary' } })
    expect(wrapper.classes()).toContain('btn-secondary')
  })

  it('applies btn-ghost class when variant="ghost"', () => {
    const wrapper = mount(CoButton, { props: { variant: 'ghost' } })
    expect(wrapper.classes()).toContain('btn-ghost')
  })

  it('renders as a <button> element by default', () => {
    const wrapper = mount(CoButton)
    expect(wrapper.element.tagName).toBe('BUTTON')
  })

  it('renders as an <a> element when tag="a"', () => {
    const wrapper = mount(CoButton, { props: { tag: 'a', href: '/about' } })
    expect(wrapper.element.tagName).toBe('A')
  })

  it('is disabled when disabled prop is true', () => {
    const wrapper = mount(CoButton, { props: { disabled: true } })
    expect(wrapper.attributes('disabled')).toBeDefined()
  })

  it('emits click event', async () => {
    const wrapper = mount(CoButton)
    await wrapper.trigger('click')
    expect(wrapper.emitted('click')).toHaveLength(1)
  })

  it('does not emit click when disabled', async () => {
    const wrapper = mount(CoButton, { props: { disabled: true } })
    await wrapper.trigger('click')
    // disabled buttons should not emit click
    expect(wrapper.emitted('click')).toBeUndefined()
  })
})
