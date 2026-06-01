/**
 * tests/pages/SettingsPage.test.ts — TDD tests for the admin settings page
 *
 * What it does:
 *   Verifies the settings page loads current config values, allows editing
 *   the prayer chain email address, and configures the Phase 6 email connector
 *   (provider selector + MS365 credential fields).
 *
 * How it connects:
 *   Component under test: app/pages/settings/index.vue
 *   API calls: GET /site-config/{key}, PUT /site-config/{key}
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
    // onMounted makes 5 GET calls; mock them all, then the PUT
    const fetchMock = vi.fn().mockResolvedValue(MOCK_EMAIL_CONFIG)
    vi.stubGlobal('$fetch', fetchMock)

    const wrapper = mountPage()
    await flushPromises()

    await wrapper.find('input[name="prayer_chain_email"]').setValue('new@libbynaz.org')
    await wrapper.find('[data-testid="prayer-form"]').trigger('submit')
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
    // onMounted makes 5 GET calls; provide resolved values for each,
    // then reject the prayer chain PUT (call 6)
    const fetchMock = vi.fn()
      .mockResolvedValueOnce(MOCK_EMAIL_CONFIG)        // 1: GET prayer_chain_email
      .mockResolvedValueOnce({ value: 'smtp' })        // 2: GET email_provider
      .mockResolvedValueOnce({ value: '' })            // 3: GET ms365_tenant_id
      .mockResolvedValueOnce({ value: '' })            // 4: GET ms365_client_id
      .mockResolvedValueOnce({ value: '' })            // 5: GET ms365_sender
      .mockRejectedValueOnce(new Error('Network error')) // 6: PUT prayer_chain_email
    vi.stubGlobal('$fetch', fetchMock)

    const wrapper = mountPage()
    await flushPromises()

    await wrapper.find('[data-testid="prayer-form"]').trigger('submit')
    await flushPromises()

    expect(wrapper.text()).toMatch(/error|failed/i)
  })
})

// ---------------------------------------------------------------------------
// Phase 6 — Email Connector section
// ---------------------------------------------------------------------------
describe('SettingsPage — Email Connector', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.stubGlobal('$fetch', vi.fn().mockResolvedValue({ value: 'smtp' }))
  })

  it('renders the email connector section', async () => {
    const wrapper = mountPage()
    await flushPromises()
    expect(wrapper.find('[data-testid="connector-section"]').exists()).toBe(true)
  })

  it('shows a provider dropdown defaulting to smtp', async () => {
    const wrapper = mountPage()
    await flushPromises()
    const select = wrapper.find('[data-testid="email-provider-select"]')
    expect(select.exists()).toBe(true)
    expect((select.element as HTMLSelectElement).value).toBe('smtp')
  })

  it('hides MS365 fields when smtp is selected', async () => {
    const wrapper = mountPage()
    await flushPromises()
    expect(wrapper.find('[data-testid="ms365-tenant-id"]').exists()).toBe(false)
  })

  it('shows MS365 credential fields when ms365 is selected', async () => {
    const wrapper = mountPage()
    await flushPromises()
    const select = wrapper.find('[data-testid="email-provider-select"]')
    await select.setValue('ms365')
    await wrapper.vm.$nextTick()
    expect(wrapper.find('[data-testid="ms365-tenant-id"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="ms365-client-id"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="ms365-client-secret"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="ms365-sender"]').exists()).toBe(true)
  })

  it('shows SMTP env var hint when smtp is selected', async () => {
    const wrapper = mountPage()
    await flushPromises()
    expect(wrapper.text()).toMatch(/SMTP_HOST/i)
  })

  it('calls PUT /site-config/email_provider on connector save', async () => {
    const fetchMock = vi.fn().mockResolvedValue({ value: 'smtp' })
    vi.stubGlobal('$fetch', fetchMock)

    const wrapper = mountPage()
    await flushPromises()

    await wrapper.find('[data-testid="connector-form"]').trigger('submit')
    await flushPromises()

    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining('email_provider'),
      expect.objectContaining({ method: 'PUT' }),
    )
  })

  it('shows success message after connector save', async () => {
    vi.stubGlobal('$fetch', vi.fn().mockResolvedValue({ value: 'smtp' }))
    const wrapper = mountPage()
    await flushPromises()

    await wrapper.find('[data-testid="connector-save-btn"]').trigger('click')
    await flushPromises()

    expect(wrapper.find('[data-testid="connector-saved"]').isVisible()).toBe(true)
  })

  it('shows error when connector save fails', async () => {
    const fetchMock = vi.fn()
      .mockResolvedValue({ value: 'smtp' })     // onMounted calls
      .mockRejectedValueOnce(new Error('fail')) // connector PUT
    vi.stubGlobal('$fetch', fetchMock)

    const wrapper = mountPage()
    await flushPromises()

    await wrapper.find('[data-testid="connector-save-btn"]').trigger('click')
    await flushPromises()

    expect(wrapper.find('[data-testid="connector-error"]').isVisible()).toBe(true)
  })
})
