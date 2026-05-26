/**
 * packages/ui/src/tests/CoScriptureCallout.test.ts — TDD anchor for CoScriptureCallout.
 *
 * Written BEFORE CoScriptureCallout.vue exists. These tests must fail first.
 */

import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import CoScriptureCallout from '../components/CoScriptureCallout.vue'

describe('CoScriptureCallout', () => {
  it('renders slot content as the scripture text', () => {
    const wrapper = mount(CoScriptureCallout, {
      slots: { default: 'For God so loved the world...' },
    })
    expect(wrapper.text()).toContain('For God so loved the world...')
  })

  it('has scripture-callout class', () => {
    const wrapper = mount(CoScriptureCallout)
    expect(wrapper.classes()).toContain('scripture-callout')
  })

  it('renders the reference when provided', () => {
    const wrapper = mount(CoScriptureCallout, {
      props: { reference: 'John 3:16' },
      slots: { default: 'For God so loved the world...' },
    })
    expect(wrapper.text()).toContain('John 3:16')
  })

  it('renders as a <blockquote> element', () => {
    const wrapper = mount(CoScriptureCallout)
    expect(wrapper.element.tagName).toBe('BLOCKQUOTE')
  })
})
