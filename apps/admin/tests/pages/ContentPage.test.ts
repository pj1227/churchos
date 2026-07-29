/**
 * tests/pages/ContentPage.test.ts — TDD tests for the admin Site Content page
 *
 * What it does:
 *   Verifies the page loads existing site_config values in one bulk GET,
 *   pre-fills form fields, saves each field via PUT /site-config/{key}
 *   with is_public=true (except logos_feed_url, which is staff-only), and
 *   supports uploading a logo via POST /site-config/logo.
 *
 * How it connects:
 *   Component under test: app/pages/content/index.vue
 *   API calls: GET /site-config, PUT /site-config/{key}, POST /site-config/logo
 */

import { mount, flushPromises } from '@vue/test-utils'
import { setActivePinia, createPinia } from 'pinia'
import { describe, it, expect, beforeEach, vi } from 'vitest'
import ContentPage from '~/pages/content/index.vue'

const MOCK_ROWS = [
  { id: 1, church_id: 'default', key: 'church_name', value: 'Libby Church of the Nazarene', is_secret: false, is_json: false, is_public: true, updated_at: '2026-07-28T10:00:00Z' },
  { id: 2, church_id: 'default', key: 'church_phone', value: '(406) 293-2931', is_secret: false, is_json: false, is_public: true, updated_at: '2026-07-28T10:00:00Z' },
  { id: 3, church_id: 'default', key: 'church_logo_url', value: 'https://test.supabase.co/storage/v1/object/public/public-assets/logo-abc.png', is_secret: false, is_json: false, is_public: true, updated_at: '2026-07-28T10:00:00Z' },
]

function mountPage() {
  return mount(ContentPage, {
    global: {
      stubs: {
        NuxtLink: { template: '<a :href="to"><slot /></a>', props: ['to'] },
      },
    },
  })
}

beforeEach(() => {
  setActivePinia(createPinia())
  vi.stubGlobal('$fetch', vi.fn().mockResolvedValue(MOCK_ROWS))
})

describe('ContentPage', () => {
  it('renders a "Site Content" heading', async () => {
    const wrapper = mountPage()
    await flushPromises()
    expect(wrapper.text()).toMatch(/site content/i)
  })

  it('loads and pre-fills existing values from a single GET /site-config call', async () => {
    const fetchMock = vi.fn().mockResolvedValue(MOCK_ROWS)
    vi.stubGlobal('$fetch', fetchMock)

    const wrapper = mountPage()
    await flushPromises()

    expect(fetchMock).toHaveBeenCalledWith('/site-config')
    const input = wrapper.find('input[name="church_name"]')
    expect((input.element as HTMLInputElement).value).toBe('Libby Church of the Nazarene')
  })

  it('renders every documented CMS section', async () => {
    const wrapper = mountPage()
    await flushPromises()
    for (const title of [
      'Church Identity', 'Location', 'Contact Information', 'Service Times',
      'Home Page', 'About Page', 'Sermons Page', 'Giving Page', 'Sermon Feed (Logos)',
    ]) {
      expect(wrapper.find(`[data-testid="section-${title}"]`).exists()).toBe(true)
    }
  })

  it('shows a logo preview when church_logo_url is set', async () => {
    const wrapper = mountPage()
    await flushPromises()
    const preview = wrapper.find('[data-testid="logo-preview"]')
    expect(preview.exists()).toBe(true)
    expect(preview.attributes('src')).toContain('logo-abc.png')
  })

  it('uploads a logo file via POST /site-config/logo', async () => {
    const fetchMock = vi.fn()
      .mockImplementation((url: string, opts?: { method?: string }) => {
        if (url === '/site-config/logo' && opts?.method === 'POST') {
          return Promise.resolve({ url: 'https://test.supabase.co/storage/v1/object/public/public-assets/logo-new.png' })
        }
        return Promise.resolve(MOCK_ROWS)
      })
    vi.stubGlobal('$fetch', fetchMock)

    const wrapper = mountPage()
    await flushPromises()

    const file = new File(['fake-bytes'], 'logo.png', { type: 'image/png' })
    const input = wrapper.find('[data-testid="logo-file-input"]')
    Object.defineProperty(input.element, 'files', { value: [file] })
    await input.trigger('change')
    await flushPromises()

    expect(fetchMock).toHaveBeenCalledWith('/site-config/logo', expect.objectContaining({ method: 'POST' }))
    expect(wrapper.find('[data-testid="logo-preview"]').attributes('src')).toContain('logo-new.png')
  })

  it('saves every field via PUT with is_public=true for content keys', async () => {
    const fetchMock = vi.fn().mockResolvedValue(MOCK_ROWS)
    vi.stubGlobal('$fetch', fetchMock)

    const wrapper = mountPage()
    await flushPromises()

    await wrapper.find('[data-testid="content-form"]').trigger('submit')
    await flushPromises()

    expect(fetchMock).toHaveBeenCalledWith(
      '/site-config/church_name',
      expect.objectContaining({ method: 'PUT', body: expect.objectContaining({ is_public: true }) }),
    )
  })

  it('saves logos_feed_url with is_public=false', async () => {
    const fetchMock = vi.fn().mockResolvedValue(MOCK_ROWS)
    vi.stubGlobal('$fetch', fetchMock)

    const wrapper = mountPage()
    await flushPromises()

    await wrapper.find('[data-testid="content-form"]').trigger('submit')
    await flushPromises()

    expect(fetchMock).toHaveBeenCalledWith(
      '/site-config/logos_feed_url',
      expect.objectContaining({ method: 'PUT', body: expect.objectContaining({ is_public: false }) }),
    )
  })

  it('shows success message after saving', async () => {
    vi.stubGlobal('$fetch', vi.fn().mockResolvedValue(MOCK_ROWS))
    const wrapper = mountPage()
    await flushPromises()

    await wrapper.find('[data-testid="content-form"]').trigger('submit')
    await flushPromises()

    expect(wrapper.text()).toMatch(/saved|success/i)
  })

  it('shows error message when a save fails', async () => {
    const fetchMock = vi.fn()
      .mockImplementation((url: string, opts?: { method?: string }) => {
        if (opts?.method === 'PUT') return Promise.reject(new Error('Network error'))
        return Promise.resolve(MOCK_ROWS)
      })
    vi.stubGlobal('$fetch', fetchMock)

    const wrapper = mountPage()
    await flushPromises()

    await wrapper.find('[data-testid="content-form"]').trigger('submit')
    await flushPromises()

    expect(wrapper.text()).toMatch(/error|failed/i)
  })
})
