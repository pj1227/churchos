/**
 * tests/pages/SettingsPage.test.ts — TDD tests for the admin settings page
 *
 * What it does:
 *   Verifies the settings page loads current config values, allows editing
 *   the prayer chain email address, and saves via PUT /site-config/{key}.
 *
 * How it connects:
 *   Component under test: app/pages/settings/index.vue
 *   API calls: GET /site-config/prayer_chain_email, PUT /site-config/prayer_chain_email
 */

import { mount, flushPromises } from '@vue/test-utils'
import { setActivePinia, createPinia } from 'pinia'
import { describe, it, expect, beforeEach, vi } from 'vitest'
import SettingsPage from '~/pages/settings/index.vue'

const MOCK_EMAIL_CONFIG = {
  id:         1,
  church_id:  'default',
  key:        'prayer_chain_email',
  value:      'prayer@libbynaz.org',
  is_secret:  false,
  is_json:    false,
  updated_at: '2026-05-29T10:00:00Z',
}

function mountPage() {
  return mount(SettingsPage, {
    global: {
      stubs: {
        NuxtLink: { template: '<a :href="to"><slot /></a>', props: ['to'] },
      },
    },
  })
}

beforeEach(() => {
  setActivePinia(createPinia())
  vi.stubGlobal('$fetch', vi.fn().mockResolvedValue(MOCK_EMAIL_CONFIG))
})

describe('SettingsPage', () => {
  it('renders a "Settings" heading', async () => {
    const wrapper = mountPage()
    await flushPromises()
    expect(wrapper.text()).toMatch(/settings/i)
  })

  it('renders a prayer chain email section', async () => {
    const wrapper = mountPage()
    await flushPromises()
    expect(wrapper.text()).toMatch(/prayer chain/i)
  })

  it('loads and pre-fills the current prayer chain email', async () => {
    const wrapper = mountPage()
    await flushPromises()
    const input = wrapper.find('input[name="prayer_chain_email"]')
    expect(input.exists()).toBe(true)
    expect((input.element as HTMLInputElement).value).toBe('prayer@libbynaz.org')
  })

  it('has a save button', async () => {
    const wrapper = mountPage()
    await flushPromises()
    expect(wrapper.find('button[type="submit"], button').exists()).toBe(true)
  })

  it('calls PUT /site-config/prayer_chain_email on save', async () => {
    const fetchMock = vi.fn()
      .mockResolvedValueOnce(MOCK_EMAIL_CONFIG)
      .mockResolvedValueOnce({ ...MOCK_EMAIL_CONFIG, value: 'new@libbynaz.org' })
    vi.stubGlobal('$fetch', fetchMock)

    const wrapper = mountPage()
    await flushPromises()

    await wrapper.find('input[name="prayer_chain_email"]').setValue('new@libbynaz.org')
    await wrapper.find('form').trigger('submit')
    await flushPromises()

    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining('prayer_chain_email'),
      expect.objectContaining({ method: 'PUT' }),
    )
  })

  it('shows success message after saving', async () => {
    const fetchMock = vi.fn()
      .mockResolvedValueOnce(MOCK_EMAIL_CONFIG)
      .mockResolvedValueOnce({ ...MOCK_EMAIL_CONFIG, value: 'new@libbynaz.org' })
    vi.stubGlobal('$fetch', fetchMock)

    const wrapper = mountPage()
    await flushPromises()

    await wrapper.find('form').trigger('submit')
    await flushPromises()

    expect(wrapper.text()).toMatch(/saved|success/i)
  })

  it('shows error message when save fails', async () => {
    const fetchMock = vi.fn()
      .mockResolvedValueOnce(MOCK_EMAIL_CONFIG)
      .mockRejectedValueOnce(new Error('Network error'))
    vi.stubGlobal('$fetch', fetchMock)

    const wrapper = mountPage()
    await flushPromises()

    await wrapper.find('form').trigger('submit')
    await flushPromises()

    expect(wrapper.text()).toMatch(/error|failed/i)
  })
})
