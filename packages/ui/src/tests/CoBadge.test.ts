/**
 * packages/ui/src/tests/CoBadge.test.ts — TDD anchor for CoBadge.
 *
 * Written BEFORE CoBadge.vue exists. These tests must fail first.
 */

import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import CoBadge from '../components/CoBadge.vue'

describe('CoBadge', () => {
  it('renders slot content', () => {
    const wrapper = mount(CoBadge, { slots: { default: 'Sermon' } })
    expect(wrapper.text()).toBe('Sermon')
  })

  it('applies badge-forest class by default', () => {
    const wrapper = mount(CoBadge)
    expect(wrapper.classes()).toContain('badge-forest')
  })

  it('applies badge-kootenai class when color="kootenai"', () => {
    const wrapper = mount(CoBadge, { props: { color: 'kootenai' } })
    expect(wrapper.classes()).toContain('badge-kootenai')
  })

  it('applies badge-gold class when color="gold"', () => {
    const wrapper = mount(CoBadge, { props: { color: 'gold' } })
    expect(wrapper.classes()).toContain('badge-gold')
  })

  it('renders as a <span> element', () => {
    const wrapper = mount(CoBadge)
    expect(wrapper.element.tagName).toBe('SPAN')
  })
})
