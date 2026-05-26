/**
 * packages/ui/src/tests/CoFormInput.test.ts — TDD anchor for CoFormInput.
 *
 * Written BEFORE CoFormInput.vue exists. These tests must fail first.
 */

import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import CoFormInput from '../components/CoFormInput.vue'

describe('CoFormInput', () => {
  it('renders an <input> element', () => {
    const wrapper = mount(CoFormInput)
    expect(wrapper.find('input').exists()).toBe(true)
  })

  it('renders a <label> when label prop is provided', () => {
    const wrapper = mount(CoFormInput, { props: { label: 'Email address' } })
    expect(wrapper.find('label').exists()).toBe(true)
    expect(wrapper.find('label').text()).toBe('Email address')
  })

  it('applies form-input class to the input', () => {
    const wrapper = mount(CoFormInput)
    expect(wrapper.find('input').classes()).toContain('form-input')
  })

  it('applies form-label class to the label', () => {
    const wrapper = mount(CoFormInput, { props: { label: 'Name' } })
    expect(wrapper.find('label').classes()).toContain('form-label')
  })

  it('passes placeholder to input', () => {
    const wrapper = mount(CoFormInput, { props: { placeholder: 'Enter your name' } })
    expect(wrapper.find('input').attributes('placeholder')).toBe('Enter your name')
  })

  it('passes type to input (defaults to text)', () => {
    const wrapper = mount(CoFormInput)
    expect(wrapper.find('input').attributes('type')).toBe('text')
  })

  it('passes type="email" to input', () => {
    const wrapper = mount(CoFormInput, { props: { type: 'email' } })
    expect(wrapper.find('input').attributes('type')).toBe('email')
  })

  it('associates label with input via htmlFor / id', () => {
    const wrapper = mount(CoFormInput, { props: { label: 'Email', id: 'email' } })
    expect(wrapper.find('label').attributes('for')).toBe('email')
    expect(wrapper.find('input').attributes('id')).toBe('email')
  })

  it('emits update:modelValue on input', async () => {
    const wrapper = mount(CoFormInput)
    await wrapper.find('input').setValue('hello')
    expect(wrapper.emitted('update:modelValue')?.[0]).toEqual(['hello'])
  })

  it('is disabled when disabled prop is true', () => {
    const wrapper = mount(CoFormInput, { props: { disabled: true } })
    expect(wrapper.find('input').attributes('disabled')).toBeDefined()
  })
})
