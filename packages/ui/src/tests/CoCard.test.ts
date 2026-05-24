/**
 * packages/ui/src/tests/CoCard.test.ts — TDD anchor for CoCard and CoCardFeatured.
 *
 * Written BEFORE CoCard.vue / CoCardFeatured.vue exist. These tests must fail first.
 */

import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import CoCard from '../components/CoCard.vue'
import CoCardFeatured from '../components/CoCardFeatured.vue'

describe('CoCard', () => {
  it('renders slot content', () => {
    const wrapper = mount(CoCard, { slots: { default: '<p>Card body</p>' } })
    expect(wrapper.text()).toBe('Card body')
  })

  it('has co-card class', () => {
    const wrapper = mount(CoCard)
    expect(wrapper.classes()).toContain('co-card')
  })

  it('renders an optional title via prop', () => {
    const wrapper = mount(CoCard, { props: { title: 'Sunday Service' } })
    expect(wrapper.text()).toContain('Sunday Service')
  })
})

describe('CoCardFeatured', () => {
  it('renders slot content', () => {
    const wrapper = mount(CoCardFeatured, { slots: { default: 'Featured' } })
    expect(wrapper.text()).toBe('Featured')
  })

  it('has co-card-featured class', () => {
    const wrapper = mount(CoCardFeatured)
    expect(wrapper.classes()).toContain('co-card-featured')
  })
})
